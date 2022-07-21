import logging
import os
import sys
import webbrowser
from os import isatty
from typing import List, Sequence, Optional, Iterable
from typing import TYPE_CHECKING

# import for nuitka
# noinspection PyUnresolvedReferences
import sqlalchemy.sql.default_comparator  # noqa: F401
import typer

from twbm.bookmarks import Bookmarks, check_tags, clean_tags, parse_tags
from twbm.buku import BukuDb, edit_rec
from twbm.db.dal import DAL, Bookmark
from twbm.environment import config
from twbm.handle_uri import open_it

if TYPE_CHECKING:
    pass

_log = logging.getLogger(__name__)
log_fmt = r"%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(format=log_fmt, level=config.log_level, datefmt=datefmt)
logging.getLogger("urllib3").setLevel(logging.ERROR)

HELP_DESC = """
Generic URI manager for the command line.

Features:
- manages general URIs in sqlite database
- know how to open HTTP URLs, Microsoft Office Files, Images, ...
- can execute URIs as shell commands via the protocol prefix: 'shell::'
   Example: shell::vim +/"## SqlAlchemy" $HOME/document.md
"""

app = typer.Typer(help=HELP_DESC)

fts_sql = """
-- name: fts
-- record_class: Bookmark
"""


def _update_tags(
    ids: Sequence[int],
    tags: Optional[Sequence[str]] = None,
    tags_not: Optional[Sequence[str]] = None,
    force: bool = False,
):
    bms = Bookmarks(fts_query="").bms
    if tags is None:
        tags = ()
    if tags_not is None:
        tags_not = ()

    with DAL(env_config=config) as dal:
        # to allow for redefinition: set -> list
        # (https://mypy.readthedocs.io/en/stable/common_issues.html#redefinitions-with-incompatible-types)
        new_tags: Iterable
        for id in ids:
            bm = bms[id - 1]
            if force:
                new_tags = set(tags)
            else:
                new_tags = (set(bm.split_tags) | set(tags)) - set(tags_not)
            new_tags = sorted(new_tags)
            new_tags_str = f",{','.join(new_tags)},"
            _log.debug(f"{new_tags_str=}")
            bm.tags = new_tags_str
            dal.update_bookmark(bm)

            show_bms((bm,))


def show_bms(bms: Sequence[Bookmark], err: bool = True, show_timestamp: bool = False):
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
            fg=typer.colors.BRIGHT_BLUE,
            err=err,
        )
        if show_timestamp:
            typer.secho(
                f"{' ':>{offset}}{bm.last_update_ts.strftime('%Y-%m-%d %H:%M:%S')}",
                fg=typer.colors.BRIGHT_BLACK,
                err=err,
            )
        typer.secho("", err=err)
        typer.secho("", err=err)


def process(bms: Sequence[Bookmark]):  # noqa: max-complexity: 18
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
    selection: List = input().split()

    try:
        # open it if no command letter
        try:
            selection = [int(x) for x in selection]
            for i in selection:
                uri = bms[i].URL
                open_it(uri)
            return
        except ValueError:
            pass

        # with command letter
        cmd = str(selection[0])
        selection = sorted([int(x) for x in selection[1:]])
        ids = []

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
    except IndexError:
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
    tags_prefix: str = typer.Option(
        None, "--prefix", help="tags to prefix the tags option"
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
    if tags_prefix is not None:
        if tags_all is None:
            tags_all = tags_prefix
        else:
            tags_all = f"{tags_all},{tags_prefix}"

    if verbose:
        typer.echo(f"{config.twbm_db_url=}, {tags_all=}", err=True)

    bms = Bookmarks(fts_query=fts_query).filter(
        tags_all, tags_all_not, tags_any, tags_any_not, tags_exact
    )

    # ordering of results
    # cast to avoid mypy error: Returning Any from function declared to return "SupportsLessThan"
    # https://github.com/python/mypy/issues/9656
    k = lambda bm: bm.last_update_ts
    if order_desc:
        bms = sorted(bms, key=k)
    elif order_asc:
        bms = sorted(bms, key=k, reverse=True)
    else:
        k = lambda bm: bm.metadata.lower() if bm.metadata else ""
        bms = sorted(bms, key=k)

    show_bms(bms, show_timestamp=order_desc or order_asc)
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
    Updates bookmarks with tags:
    either removes tags, add tags or overwrites entire taglist.

    Gotcha:
    in order to allow for piped input, ids must be separated by comma with no blanks.

    Example for using piped input:

        twbm search xxxxx | twbm update -t <tag>
    """
    if verbose:
        typer.echo(f"Using DB: {config.twbm_db_url}", err=True)
    if tags is not None:
        tags = tags.lower().replace(" ", "").split(",")  # type: ignore
    if tags_not is not None:
        tags_not = tags_not.lower().replace(" ", "").split(",")  # type: ignore

    # Gotcha: running from IDE looks like pipe
    is_pipe = not isatty(sys.stdin.fileno())

    if is_pipe:
        ids = sys.stdin.readline()

    try:
        id_list = [int(x.strip()) for x in ids.split(",")]
    except ValueError:
        typer.secho(f"-E- Wrong input format.", fg=typer.colors.RED, err=True)
        raise typer.Abort()

    print(id_list)
    _update_tags(id_list, tags, tags_not, force=force)


@app.command()
def open(
    # ctx: typer.Context,
    ids: str = typer.Argument(None, help="list of ids, separated by comma, no blanks"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    """
    Opens bookmarks

    Gotcha:
    in order to allow for piped input, ids must be separated by comma with no blanks.

    Example for using piped input:

        twbm search xxxxx | twbm open
    """
    if verbose:
        typer.echo(f"Using DB: {config.twbm_db_url}", err=True)

    # Gotcha: running from IDE looks like pipe
    is_pipe = not isatty(sys.stdin.fileno())

    if is_pipe:
        ids = sys.stdin.readline()

    try:
        ids = [int(x.strip()) for x in ids.split(",")]  # type: ignore
    except ValueError:
        typer.secho(f"-E- Wrong input format.", fg=typer.colors.RED, err=True)
        raise typer.Abort()

    print(ids)
    with DAL(env_config=config) as dal:
        for id_ in ids:
            bm = dal.get_bookmark_by_id(id_=id_)
            show_bms((bm,))
            # TODO: generalize opening URI
            if bm.URL.startswith("http"):
                webbrowser.open(bm.URL, new=2)
            else:
                open_it(bm.URL)
                # typer.secho(
                #     "-W- Only HTTP implemented for direct open.",
                #     fg=typer.colors.RED,
                #     err=True,
                # )


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
        # Adding URL
        twbm add https://www.google.com tag1, tag2 --title "<title>"

        # Adding URI to local files (uses platform standard to open file)
        twmb add '$HOME/vimwiki/e4m/poker-points.png' --title 'Poker Points'

        # Adding shell commands as URI
        twbm add "shell::vim +/'# SqlAlchemy' sql.md" shell,sql,doc --title 'sqlalchemy snippets'
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
                fg=typer.colors.RED,
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

    # _ = BukuDb(dbfile=config.dbfile).print_rec(index=id_)  # noqa E800
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
        help=(
            "tag for which related tags should be shown. No input: all tags are"
            " printed."
        ),
    ),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    """
    No parameter: Show all tags

    With tag as parameter:
    Show related tags, i.e. tags which are used in combination with tag.
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


if __name__ == "__main__":
    _log.debug(config)
    app()
