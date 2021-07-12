import sys
import webbrowser
from os import isatty
from typing import Sequence

import typer

from db.dal import DAL, Bookmark

import logging

from twbm.environment import config

_log = logging.getLogger(__name__)
log_fmt = r'%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s'
datefmt = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(format=log_fmt, level=config.log_level, datefmt=datefmt)

app = typer.Typer()

fts_sql = """
-- name: fts
-- record_class: Bookmark
"""


def match_all_tags(tags: Sequence, bm_tags: Sequence) -> bool:
    return (set(bm_tags) & set(tags)) == set(tags)


def match_any_tag(tags: Sequence, bm_tags: Sequence) -> bool:
    return len(set(bm_tags) & set(tags)) > 0


class Bookmarks:
    bms: Sequence[Bookmark]

    def __init__(self, fts_query: str):
        self.fts_query = fts_query

        with DAL(env_config=config) as dal:
            self.bms = dal.get_bookmarks(fts_query=fts_query)

    @staticmethod
    def match_all(tags: Sequence[str], bms: Sequence[Bookmark], not_: bool = False) -> Sequence[Bookmark]:
        if not_:
            filtered = [bm for bm in bms if not match_all_tags(tags, bm.split_tags)]
        else:
            filtered = [bm for bm in bms if match_all_tags(tags, bm.split_tags)]
        return filtered

    @staticmethod
    def match_any(tags: Sequence[str], bms: Sequence[Bookmark], not_: bool = False) -> Sequence[Bookmark]:
        if not_:
            filtered = [bm for bm in bms if not match_any_tag(tags, bm.split_tags)]
        else:
            filtered = [bm for bm in bms if match_any_tag(tags, bm.split_tags)]
        return filtered


def show_bms(bms: Sequence[Bookmark]):
    for i, bm in enumerate(bms):
        offset = len(str(i)) + 2

        bmid_formatted = typer.style(f"{bm.id}", fg=typer.colors.BRIGHT_BLACK, bold=False)
        bmtitle_formatted = typer.style(f"{i}. {bm.metadata}", fg=typer.colors.GREEN, bold=True)
        typer.echo(f"{bmtitle_formatted} [{bmid_formatted}]")

        typer.secho(f"{' ':>{offset}}{bm.URL}", fg=typer.colors.YELLOW)
        if bm.desc != "":
            typer.secho(f"{' ':>{offset}}{bm.desc}", fg=None)
        typer.secho(f"{' ':>{offset}}{', '.join((tag for tag in bm.split_tags if tag != ''))}", fg=typer.colors.BLUE)
        typer.secho()
        typer.secho()


def process(bms: Sequence[Bookmark]):
    typer.secho(f"Selection: ", fg=typer.colors.GREEN)
    selection = [x for x in input().split()]

    # open in browser
    try:
        selection = [int(x) for x in selection]
        for i in selection:
            webbrowser.open(bms[i].URL, new=2)
        return
    except ValueError as e:
        pass

    # other commands
    cmd = str(selection[0])
    selection = [int(x) for x in selection[1:]]
    ids = list()
    if cmd == 'p':
        if len(selection) == 0:
            ids = [bm.id for bm in bms]
        else:
            for i in selection:
                ids.append(bms[i].id)

        typer.echo(" ".join((str(x) for x in ids)))
    else:
        typer.secho(f"-E- Invalid command {cmd}")


@app.command()
def search(
        # ctx: typer.Context,
        fts_query: str = typer.Argument("", help="FTS query"),
        tags_all: str = typer.Option("", '-t', '--tags', help="match all, comma seperated list"),
        tags_any: str = typer.Option("", '-T', '--Tags', help="match any, comma seperated list"),
        tags_all_not: str = typer.Option("", '-n', '--tags', help="not match all, comma seperated list"),
        tags_any_not: str = typer.Option("", '-N', '--Tags', help="not match any, comma seperated list"),
        non_interactive: bool = typer.Option(False, '--np', help="do not prompt for opening URLs"),
        verbose: bool = typer.Option(False, '-v', '--verbose'),
):
    if verbose:
        typer.echo(f"Using DB: {config.bm_db_url}")
    tags_all_ = tags_all.lower().replace(" ", "").split(',')
    tags_any_ = tags_any.lower().replace(" ", "").split(',')
    tags_all_not_ = tags_all_not.lower().replace(" ", "").split(',')
    tags_any_not_ = tags_any_not.lower().replace(" ", "").split(',')

    # generate FTS full list for further tag filtering
    bms = Bookmarks(fts_query=fts_query).bms

    # 1. select viable
    if tags_all != "":
        bms = Bookmarks.match_all(tags_all_, bms)

    if tags_any != "":
        bms = Bookmarks.match_any(tags_any_, bms)

    # 2. narrow down
    if tags_any_not != "":
        bms = Bookmarks.match_any(tags_any_not_, bms, not_=True)

    if tags_all_not != "":
        bms = Bookmarks.match_all(tags_all_not_, bms, not_=True)

    show_bms(bms)
    typer.echo(f"Found: {len(bms)}")

    if not non_interactive:
        process(bms)


@app.command()
def delete(
        # ctx: typer.Context,
        id_: int = typer.Argument(..., help="match all, comma seperated list"),
        verbose: bool = typer.Option(False, '-v', '--verbose'),
):
    if verbose:
        typer.echo(f"Using DB: {config.bm_db_url}")

    dal = DAL(env_config=config)
    with dal as dal:
        result = dal.delete_bookmark(id_)
        typer.echo(f"Deleted: {result}")


def _update_tags(ids: Sequence[int], tags: Sequence[str] = None, tags_not: Sequence[str] = None, force: bool = False):
    bms = Bookmarks(fts_query="").bms
    if tags is None: tags = ('',)
    if tags_not is None: tags_not = ('',)

    dal = DAL(env_config=config)
    with dal as dal:
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


@app.command()
def update(
        # ctx: typer.Context,
        input_: str = typer.Argument(None, help="tags, comma seperated list, no blanks"),
        tags: str = typer.Option("", '-t', '--tags', help="add taglist to tags"),
        tags_not: str = typer.Option("", '-n', '--tags', help="remove taglist from tags"),
        force: bool = typer.Option(False, '-f', '--force', help='overwrite tags with taglist'),
        verbose: bool = typer.Option(False, '-v', '--verbose'),

):
    if verbose:
        typer.echo(f"Using DB: {config.bm_db_url}")
    tags_ = tags.lower().replace(" ", "").split(',')
    tags_not_ = tags_not.lower().replace(" ", "").split(',')

    # Gotcha: running from IDE looks like pipe
    is_pipe = not isatty(sys.stdin.fileno())
    ids: Sequence[int] = list()

    if is_pipe:
        input_ = sys.stdin.readline()

    try:
        ids = [int(x) for x in input_.split()]
    except ValueError as e:
        typer.secho(f"-E- Wrong input format.", color=typer.colors.RED)
        raise typer.Abort()

    _update_tags(ids, tags_, tags_not_, force=force)


if __name__ == "__main__":
    _log.debug("xxxxxxxxxxx")
    app()
