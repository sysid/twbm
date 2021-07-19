import logging
import os
import sys
import webbrowser
from os import isatty
from typing import Sequence, List

import typer

from twbm.buku import edit_rec, BukuDb
from twbm.db.dal import Bookmark, DAL
from twbm.environment import config

_log = logging.getLogger(__name__)
log_fmt = r"%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(format=log_fmt, level=config.log_level, datefmt=datefmt)
logging.getLogger("urllib3").setLevel(logging.WARNING)

app = typer.Typer()

fts_sql = """
-- name: fts
-- record_class: Bookmark
"""


def clean_tags(raw_tags: Sequence[str]) -> Sequence[str]:
    tags = set()
    tags_ = set(tag.strip().strip(",").lower() for tag in raw_tags)
    for tag in tags_:
        tags__ = set(t for t in tag.split(",") if t != ",")
        tags |= tags__
    tags = sorted(tags)
    _log.debug(f"cleaned tags: {tags}")
    return tags


def parse_tags(tags: Sequence[str]) -> str:
    tags = sorted(set((tag.lower().strip() for tag in tags)))
    return f",{','.join(tags)},"


def match_exact_tags(tags: Sequence, bm_tags: Sequence) -> bool:
    return set(bm_tags) == set(tags)


def match_all_tags(tags: Sequence, bm_tags: Sequence) -> bool:
    return (set(bm_tags) & set(tags)) == set(tags)


def match_any_tag(tags: Sequence, bm_tags: Sequence) -> bool:
    return len(set(bm_tags) & set(tags)) > 0


def check_tags(tags: Sequence[str]) -> Sequence[str]:
    with DAL(env_config=config) as dal:
        all_tags = set(dal.get_all_tags())
        return sorted((set(tags) - all_tags))


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


class Bookmarks:
    bms: Sequence[Bookmark]

    def __init__(self, fts_query: str):
        self.fts_query = fts_query

        with DAL(env_config=config) as dal:
            self.bms = dal.get_bookmarks(fts_query=fts_query)

    @staticmethod
    def match_all(
        tags: Sequence[str], bms: Sequence[Bookmark], not_: bool = False
    ) -> Sequence[Bookmark]:
        if not_:
            filtered = [bm for bm in bms if not match_all_tags(tags, bm.split_tags)]
        else:
            filtered = [bm for bm in bms if match_all_tags(tags, bm.split_tags)]
        return filtered

    @staticmethod
    def match_any(
        tags: Sequence[str], bms: Sequence[Bookmark], not_: bool = False
    ) -> Sequence[Bookmark]:
        if not_:
            filtered = [bm for bm in bms if not match_any_tag(tags, bm.split_tags)]
        else:
            filtered = [bm for bm in bms if match_any_tag(tags, bm.split_tags)]
        return filtered

    @staticmethod
    def match_exact(
        tags: Sequence[str], bms: Sequence[Bookmark], not_: bool = False
    ) -> Sequence[Bookmark]:
        if not_:
            filtered = [bm for bm in bms if not match_exact_tags(tags, bm.split_tags)]
        else:
            filtered = [bm for bm in bms if match_exact_tags(tags, bm.split_tags)]
        return filtered


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
    typer.secho(f"Selection: ", fg=typer.colors.GREEN, err=True)
    selection = [x for x in input().split()]

    try:
        # open in browser if no command letter
        try:
            selection = [int(x) for x in selection]
            for i in selection:
                webbrowser.open(bms[i].URL, new=2)
            return
        except ValueError as e:
            pass

        # with command letter
        cmd = str(selection[0])
        selection = sorted([int(x) for x in selection[1:]])
        ids = list()

        if cmd == "p":
            if len(selection) == 0:
                ids = [bm.id for bm in bms]
            else:
                for i in selection:
                    ids.append(bms[i].id)
            typer.echo(",".join((str(x) for x in ids)), err=False)  # stdout for piping

        elif cmd == "d":
            if len(selection) == 0:
                typer.echo(f"-W- no selection. Do nothing.")
                raise typer.Exit()
            else:
                for id_ in reversed(
                    selection
                ):  # must be reversed because of compacting
                    print(id_)
                    _ = BukuDb(dbfile=config.dbfile).delete_rec(
                        index=id_, delay_commit=False
                    )
                    typer.echo(
                        f"-M- Deleted entry: {bms[id_].metadata}: {bms[id_].URL}"
                    )

        else:
            typer.secho(f"-E- Invalid command {cmd}", err=True)
    except IndexError as e:
        typer.secho(
            f"-E- Selected index {selection} out of range.",
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
        twbm search xxxxx | twbm update -t x\n
    """
    if verbose:
        typer.echo(f"Using DB: {config.twbm_db_url}", err=True)

    tags_all_ = normalize_tag_string(tags_all)
    tags_any_ = normalize_tag_string(tags_any)
    tags_all_not_ = normalize_tag_string(tags_all_not)
    tags_any_not_ = normalize_tag_string(tags_any_not)
    tags_exact_ = normalize_tag_string(tags_exact)

    # generate FTS full list for further tag filtering
    bms = Bookmarks(fts_query=fts_query).bms

    # 0. over-rule
    if tags_exact is not None:
        bms = Bookmarks.match_exact(tags_exact_, bms)
    else:
        # 1. select viable
        if tags_all is not None:
            bms = Bookmarks.match_all(tags_all_, bms)

        if tags_any is not None:
            bms = Bookmarks.match_any(tags_any_, bms)

        # 2. narrow down
        if tags_any_not is not None:
            bms = Bookmarks.match_any(tags_any_not_, bms, not_=True)

        if tags_all_not is not None:
            bms = Bookmarks.match_all(tags_all_not_, bms, not_=True)

    # ordering of results
    if order_desc:
        bms = sorted(bms, key=lambda bm: bm.last_update_ts)
    elif order_asc:
        bms = list(reversed(sorted(bms, key=lambda bm: bm.last_update_ts)))
    else:
        bms = sorted(bms, key=lambda bm: bm.metadata.lower())

    show_bms(bms)
    typer.echo(f"Found: {len(bms)}", err=True)

    if not non_interactive:
        process(bms)


def normalize_tag_string(tag_string: str = None) -> Sequence[str]:
    if tag_string is None:
        tags_ = tuple()
    else:
        tags_ = tag_string.lower().replace(" ", "").split(",")
        tags_ = sorted(tag for tag in tags_ if tag != "")
    return tags_


@app.command()
def delete(
    # ctx: typer.Context,
    id_: int = typer.Argument(..., help="id to delete"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    if verbose:
        typer.echo(f"Using DB: {config.twbm_db_url}", err=True)

    # use buku because of DB compactdb
    _ = BukuDb(dbfile=config.dbfile).delete_rec(index=id_, delay_commit=False)

    # with DAL(env_config=config) as dal:
    #     result = dal.delete_bookmark(id=id_)
    #     typer.echo(f"Deleted index: {result}")


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
def add(
    # ctx: typer.Context,
    url_data: List[str] = typer.Argument(..., help="URL and tags"),
    title: str = typer.Option("", "--title"),
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

    _ = BukuDb(dbfile=config.dbfile).add_rec(
        url=url,
        title_in=title,
        tags_in=tags_in,
        desc=desc,
        immutable=0,
        delay_commit=False,
        fetch=(not nofetch),
    )


@app.command()
def show(
    # ctx: typer.Context,
    id_: int = typer.Argument(..., help="id to print"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
):
    if verbose:
        typer.echo(f"Using DB: {config.twbm_db_url}", err=True)
    _ = BukuDb(dbfile=config.dbfile).print_rec(index=id_)


@app.command()
def write(
    # ctx: typer.Context,
    id_: int = typer.Argument(..., help="id to print"),
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
        output = "\n".join(tags)
        typer.echo(f"{output}", err=True)


if __name__ == "__main__":
    _log.debug(config)
    app()
