import logging
import os
import sys
import webbrowser
from os import isatty
from typing import Sequence, List

# import for nuitka
# noinspection PyUnresolvedReferences
import sqlalchemy.sql.default_comparator
import typer

from twbm.bookmarks import Bookmarks, clean_tags, parse_tags, check_tags
from twbm.buku import edit_rec, BukuDb
from twbm.db.dal import Bookmark, DAL
from twbm.environment import config
from twbm.handle_uri import open_it

_log = logging.getLogger(__name__)
log_fmt = r"%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(format=log_fmt, level=config.log_level, datefmt=datefmt)
logging.getLogger("urllib3").setLevel(logging.ERROR)

HELP_DESC = """
boookmark manager for the command line
"""

app = typer.Typer(help=HELP_DESC)

fts_sql = """
-- name: fts
-- record_class: Bookmark
"""


def _update_tags(
    ids: Sequence[int],
    tags: Sequence[str] = None,
    tags_not: Sequence[str] = None,
    force: bool = False,
):
    bms = Bookmarks(fts_query="").bms
    if tags is None:
        tags = ()
    if tags_not is None:
        tags_not = ()

    with DAL(env_config=config) as dal:
        for id in ids:
            bm = bms[id - 1]
            if force:
                new_tags = set(tags)
            else:
                new_tags = (set(bm.split_tags) | set(tags)) - set(tags_not)
            new_tags = sorted(list(new_tags))
            new_tags = f",{','.join(new_tags)},"
            _log.debug(f"{new_tags=}")
            bm.tags = new_tags
            dal.update_bookmark(bm)

            show_bms((bm,))


def show_bms(bms: Sequence[Bookmark], err: bool = True):
    for i, bm in enumerate(bms):
        offset = len(str(i)) + 2

        bmid_formatted = typer.style(
            f"{bm.id}", fg=typer.colors.BRIGHT_BLACK, bold=False
        )
        bmtitle_formatted = typer.style(
            f"{i}. {bm.metadata}", fg=typer.colors.GREEN, bold=True
        )
        typer.echo(f"{bmtitle_formatted} [{bmid_formatted}]", err=err)

        typer.secho(f"{' ':>{offset}}{bm.URL}", fg=typer.colors.YELLOW, err=err)
        if bm.desc != "":
            typer.secho(f"{' ':>{offset}}{bm.desc}", fg=None, err=err)
        typer.secho(
            f"{' ':>{offset}}{', '.join((tag for tag in bm.split_tags if tag != ''))}",
            fg=typer.colors.BLUE,
            err=err,
        )
        typer.secho("", err=err)
        typer.secho("", err=err)


def process(bms: Sequence[Bookmark]):
    help_text = """
        <n1> <n2>:      opens selection in browser
        p <n1> <n2>:    print id-list of selection
        p:              print all ids
        d <n1> <n2>:    delete selection
        e:              edit selection
        q:              quit
        h:              help
    """
    typer.secho(f"Selection: ", fg=typer.colors.GREEN, err=True)
    selection = [x for x in input().split()]

    try:
        # open it if no command letter
        try:
            selection = [int(x) for x in selection]
            for i in selection:
                uri = bms[i].URL
                open_it(uri)
            return
        except ValueError as e:
            pass

        # with command letter
        cmd = str(selection[0])
        selection = sorted([int(x) for x in selection[1:]])
        ids = list()

        if cmd == "p":
            if len(selection) == 0:
                ids = [bm.id for bm in bms]  # print all ids to stdout for piping
            else:
                for i in selection:
                    ids.append(bms[i].id)
            typer.echo(",".join((str(x) for x in ids)), err=False)  # stdout for piping

        elif cmd == "d":
            if len(selection) == 0:
                typer.echo(f"-W- no selection. Do nothing.")
                raise typer.Exit()
            else:
                for i in reversed(selection):  # must be reversed because of compacting
                    bm = bms[i]
                    typer.echo(bm.id)
                    _ = BukuDb(dbfile=config.dbfile).delete_rec(
                        index=bm.id, delay_commit=False
                    )
                    typer.echo(f"-M- Deleted entry: {bm.metadata}: {bm.URL}")

        elif cmd == "e":
            if len(selection) == 0:
                # typer.echo(f"-W- no selection. Do nothing.")
                # raise typer.Exit()
                for bm in bms:
                    _ = BukuDb(dbfile=config.dbfile).edit_update_rec(
                        index=bm.id, immutable=1
                    )
            else:
                for i in selection:
                    typer.echo(bms[i].id)
                    _ = BukuDb(dbfile=config.dbfile).edit_update_rec(
                        index=bms[i].id, immutable=1
                    )

        elif cmd == "h":
            typer.echo(help_text, err=True)

        elif cmd == "q":
            raise typer.Exit()

        else:
            typer.secho(f"-E- Invalid command {cmd}\n", err=True)
            typer.echo(help_text, err=True)
    except IndexError as e:
        typer.secho(
            f"-E- Selection {selection} out of range.",
            err=True,
            fg=typer.colors.RED,
        )
        raise typer.Abort()


@app.command()
def search(
    # ctx: typer.Context,
    fts_query: str = typer.Argument("", help="FTS query"),
    tags_exact: str = typer.Option(
        None, "-e", "--exact", help="match exact, comma separated list"
    ),
    tags_all: str = typer.Option(
        None, "-t", "--tags", help="match all, comma separated list"
    ),
    tags_any: str = typer.Option(
        None, "-T", "--Tags", help="match any, comma separated list"
    ),
    tags_all_not: str = typer.Option(
        None, "-n", "--ntags", help="not match all, comma separated list"
    ),
    tags_any_not: str = typer.Option(
        None, "-N", "--Ntags", help="not match any, comma separated list"
    ),
    non_interactive: bool = typer.Option(False, "--np", help="no prompt"),
    order_desc: bool = typer.Option(False, "-o", help="order by age, descending."),
    order_asc: bool = typer.Option(False, "-O", help="order by age, ascending."),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    """
    Searches bookmark database with full text search capabilities (FTS)
    (see: https://www.sqlite.org/fts5.html)

    Title, URL and description are FTS indexed. Tags are not part of FTS.

    Tags must be specified as comma separated list without blanks.
    Correct FTS search syntax: https://www.sqlite.org/fts5.html chapter 3.

    Example:\n
        twbm search 'security "single-page"'\n
        twbm search '"https://securit" *'\n
        twbm search '^security'\n
        twbm search 'postgres OR sqlite'\n
        twbm search 'security NOT keycloak'\n
        twbm search -t tag1,tag2 -n notag1 <searchquery>\n
        twbm search -e tag1,tag2\n
        twbm search xxxxx | twbm update -t x (interactive selection)\n

    \nCommands in interactive mode:\n
        <n1> <n2>:      opens selection in browser\n
        p <n1> <n1>:    prints corresponding id-list of selection\n
        p:              prints all ids\n
        d <n1> <n1>:    delete selection\n

            p <n1> <n2>:    print id-list of selection
            p:              print all ids
            d <n1> <n2>:    delete selection
            h:              help
    """
    if verbose:
        typer.echo(f"Using DB: {config.twbm_db_url}", err=True)

    bms = Bookmarks(fts_query=fts_query).filter(
        tags_all, tags_all_not, tags_any, tags_any_not, tags_exact
    )

    # ordering of results
    if order_desc:
        bms = sorted(bms, key=lambda bm: bm.last_update_ts)
    elif order_asc:
        bms = list(reversed(sorted(bms, key=lambda bm: bm.last_update_ts)))
    else:
        bms = sorted(bms, key=lambda bm: bm.metadata.lower() if bm.metadata else "")

    show_bms(bms)
    typer.echo(f"Found: {len(bms)}", err=True)

    if not non_interactive:
        process(bms)
    else:
        ids = [bm.id for bm in bms]  # print all ids to stdout for piping
        typer.echo(",".join((str(x) for x in ids)), err=False)  # stdout for piping


@app.command()
def delete(
    # ctx: typer.Context,
    id_: int = typer.Argument(..., help="id to delete"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    if verbose:
        typer.echo(f"Using DB: {config.twbm_db_url}", err=True)

    # use buku because of DB compactdb
    with DAL(env_config=config) as dal:
        bm = dal.get_bookmark_by_id(id_=id_)
        show_bms((bm,))
    _ = BukuDb(dbfile=config.dbfile).delete_rec(index=id_, delay_commit=False)


@app.command()
def update(
    # ctx: typer.Context,
    ids: str = typer.Argument(None, help="list of ids, separated by comma, no blanks"),
    tags: str = typer.Option(None, "-t", "--tags", help="add tags to taglist"),
    tags_not: str = typer.Option(None, "-n", "--tags", help="remove tags from taglist"),
    force: bool = typer.Option(
        False, "-f", "--force", help="overwrite taglist with tags"
    ),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    """
    Updates bookmarks with tags, either removes tags, add tags or overwrites entire taglist.

    Gotcha: in order to allow for piped input, ids must be separated by comma with no blanks.

    Example for using piped input:

        twbm search xxxxx | twbm update -t <tag>
    """
    if verbose:
        typer.echo(f"Using DB: {config.twbm_db_url}", err=True)
    if tags is not None:
        tags = tags.lower().replace(" ", "").split(",")
    if tags_not is not None:
        tags_not = tags_not.lower().replace(" ", "").split(",")

    # Gotcha: running from IDE looks like pipe
    is_pipe = not isatty(sys.stdin.fileno())
    ids_: Sequence[int] = list()

    if is_pipe:
        ids = sys.stdin.readline()

    try:
        ids = [int(x.strip()) for x in ids.split(",")]
    except ValueError as e:
        typer.secho(f"-E- Wrong input format.", color=typer.colors.RED, err=True)
        raise typer.Abort()

    print(ids)
    _update_tags(ids, tags, tags_not, force=force)


@app.command()
def open(
    # ctx: typer.Context,
    ids: str = typer.Argument(None, help="list of ids, separated by comma, no blanks"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    """
    Opens bookmarks

    Gotcha: in order to allow for piped input, ids must be separated by comma with no blanks.

    Example for using piped input:

        twbm search xxxxx | twbm open
    """
    if verbose:
        typer.echo(f"Using DB: {config.twbm_db_url}", err=True)

    # Gotcha: running from IDE looks like pipe
    is_pipe = not isatty(sys.stdin.fileno())
    ids_: Sequence[int] = list()

    if is_pipe:
        ids = sys.stdin.readline()

    try:
        ids = [int(x.strip()) for x in ids.split(",")]
    except ValueError as e:
        typer.secho(f"-E- Wrong input format.", color=typer.colors.RED, err=True)
        raise typer.Abort()

    print(ids)
    with DAL(env_config=config) as dal:
        for id_ in ids:
            bm = dal.get_bookmark_by_id(id_=id_)
            show_bms((bm,))
            webbrowser.open(bm.URL, new=2)


@app.command()
def add(
    # ctx: typer.Context,
    url_data: List[str] = typer.Argument(..., help="URL and tags"),
    title: str = typer.Option(None, "--title"),
    desc: str = typer.Option("", "-d", "--desc"),
    edit: bool = typer.Option(False, "-e", "--edit", help="open in editor"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
    nofetch: bool = typer.Option(
        False, "-f", "--nofetch", help="do not try to fetch metadata from web"
    ),
):
    """
    Adds booksmarks to database and FTS index.

    Provide URL (required) and tags (optional) as parameters.

    Example:

        twbm add https://www.google.com tag1, tag2 --title "<title>"
    """
    if verbose:
        typer.echo(f"Using DB: {config.twbm_db_url}", err=True)
    url = url_data[0].strip().strip(",")
    tags = clean_tags(url_data[1:])

    if len(unknown_tags := check_tags(tags)) > 0:
        typer.confirm(f"Create {unknown_tags=} ?", abort=True)

    tags_in = parse_tags(tags)

    if edit:
        editor = os.environ.get("EDITOR", None)
        if editor is None:
            typer.secho(
                f"Editor not set, please set environment variable EDITOR",
                color=typer.colors.RED,
                err=True,
            )
            raise typer.Exit()
        result = edit_rec(
            editor=editor, url=url, title_in=title, tags_in=tags_in, desc=""
        )
        if result is not None:
            url, title, tags_in, desc_in = result
        else:
            raise typer.Abort()

    id_ = BukuDb(dbfile=config.dbfile).add_rec(
        url=url,
        title_in=title,
        tags_in=tags_in,
        desc=desc,
        immutable=0,
        delay_commit=False,
        fetch=(not nofetch),
    )
    with DAL(env_config=config) as dal:
        bm = dal.get_bookmark_by_id(id_=id_)
        show_bms((bm,))


@app.command()
def show(
    # ctx: typer.Context,
    id_: int = typer.Argument(..., help="id to print"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    if verbose:
        typer.echo(f"Using DB: {config.twbm_db_url}", err=True)

    # _ = BukuDb(dbfile=config.dbfile).print_rec(index=id_)
    with DAL(env_config=config) as dal:
        bm = dal.get_bookmark_by_id(id_=id_)
        show_bms((bm,))


@app.command()
def edit(
    # ctx: typer.Context,
    id_: int = typer.Argument(..., help="id to edit"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
    nofetch: bool = typer.Option(
        False, "-f", "--nofetch", help="do not try to fetch metadata from web"
    ),
):
    immutable = -1 if nofetch else 1
    if verbose:
        typer.echo(f"Using DB: {config.twbm_db_url}", err=True)
    _ = BukuDb(dbfile=config.dbfile).edit_update_rec(index=id_, immutable=immutable)


@app.command()
def tags(
    # ctx: typer.Context,
    tag: str = typer.Argument(
        None,
        help="tag for which related tags should be shown. No input: all tags are printed.",
    ),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    """
    No parameter: Show all tags

    With tag as parameter: Show related tags, i.e. tags which are used in combination with tag.
    """
    if verbose:
        typer.echo(f"Using DB: {config.twbm_db_url}", err=True)

    if tag is not None:
        tag = tag.strip(",").strip().lower()

    with DAL(env_config=config) as dal:
        if tag is None:
            tags = dal.get_all_tags()
        else:
            tags = dal.get_related_tags(tag=tag)
        for t in tags:
            typer.echo(f"{t[1]:>4}: {t[0]}", err=True)


@app.command()
def docs(
    # ctx: typer.Context,
    fts_query: str = typer.Argument("", help="FTS query"),
    tags_exact: str = typer.Option(
        None, "-e", "--exact", help="match exact, comma separated list"
    ),
    tags_all: str = typer.Option(
        None, "-t", "--tags", help="match all, comma separated list"
    ),
    tags_any: str = typer.Option(
        None, "-T", "--Tags", help="match any, comma separated list"
    ),
    tags_all_not: str = typer.Option(
        None, "-n", "--ntags", help="not match all, comma separated list"
    ),
    tags_any_not: str = typer.Option(
        None, "-N", "--Ntags", help="not match any, comma separated list"
    ),
    tags_prefix: str = typer.Option(
        "doc", "--prefix", help="tags to prefix the tags option"
    ),
    interactive: bool = typer.Option(False, "-i", help="interactive selection"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    """
    Searches bookmark database analog 'search' command and filters additionally for
    prefix tags. Opens 3 results in browser unless -i is specified.
    """
    if verbose:
        typer.echo(f"Using DB: {config.twbm_db_url}", err=True)

    if tags_all is None:
        tags_all = tags_prefix
    else:
        tags_all = f"{tags_all},{tags_prefix}"
    typer.echo(f"Tags: {tags_all}")
    bms = Bookmarks(fts_query=fts_query).filter(
        tags_all, tags_all_not, tags_any, tags_any_not, tags_exact
    )

    show_bms(bms)
    typer.echo(f"Found: {len(bms)}", err=True)

    if interactive or len(bms) > 3:
        process(bms)
    else:
        for bm in bms:
            webbrowser.open(bm.URL, new=2)


if __name__ == "__main__":
    _log.debug(config)
    app()
