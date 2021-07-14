import os

import pytest

from twbm import buku
from twbm.db.dal import DAL, metadata, Bookmark

os.environ[
    "RUN_ENV"
] = "testing"  # Gotcha: make sure environment setup is before app is sourced
from twbm.environment import config


@pytest.fixture()
def dal_pristine():
    dal = DAL(env_config=config)
    dal.sim_results_db_url = "sqlite:///:memory:"
    with dal as dal:
        # noinspection PyProtectedMember
        metadata.create_all(dal._sql_alchemy_db_engine)
        yield dal


def test_xxx(dal):
    _ = None


# noinspection PyTypeChecker,PyUnresolvedReferences
# @pytest.mark.skip("get real data")
def test_get_bookmarks(dal):
    results = dal.get_bookmarks(fts_query="aaa")
    # for result in results:
    #     print(f"{result.use_case}, {result.reason}, {result.strategy}")
    assert len(results) > 0
    assert isinstance(results[0], Bookmark)


def test_get_bookmarks_via_fts(dal):
    bms = dal.get_bookmarks(fts_query="aaa")
    assert len(bms) == 1


def test_get_bookmarks_raw(dal):
    bms = dal.get_bookmarks(fts_query="")
    assert len(bms) >= 5


def test_get_xxxxx(dal):
    # this is the testing entry in bm.db
    bms = dal.get_bookmarks(fts_query="xxxxx")
    assert len(bms) == 1
    assert bms[0].tags == ",ccc,xxx,yyy,"


def test_update_bm(dal):
    bm = dal.get_bookmarks(fts_query="xxxxx")[0]
    assert bm.tags == ",ccc,xxx,yyy,"

    bm.tags = ",bla,"
    result = dal.update_bookmark(bm)

    assert dal.get_bookmarks(fts_query="xxxxx")[0].tags == ",bla,"


def test_insert_bm(dal):
    bm = Bookmark(
        URL="http://ccccc/ccccc",
        metadata="metadata",
        tags=",aaa,bbb,ccc,",
        desc="description",
        flags=0,
    )
    result = dal.insert_bookmark(bm)

    assert dal.get_bookmarks(fts_query="ccccc")[0].tags == ",aaa,bbb,ccc,"


def test_delete_bm(dal):
    result = dal.delete_bookmark(id_=1)
    print(result)

    assert dal.get_bookmarks(fts_query="xxxxx")[0].id is None


def test_split_tags(dal):
    bm = Bookmark(
        URL="http://aaaaa/bbbbb",
        metadata="metadata",
        tags=",aaa,bbb,",
        desc="description",
        flags=0,
    )
    tags = bm.split_tags
    assert "" not in tags


@pytest.mark.parametrize(
    ("tag", "result"), (("ccc", ["aaa", "bbb", "ccc", "xxx", "yyy"]),)
)
def test_get_related_tags(dal, tag, result):
    tags = dal.get_related_tags(tag=tag)
    print(tags)
    assert tags == result
    assert len(tags) >= len(result)
    _ = None


def test_get_all_tags(dal):
    tags = dal.get_all_tags()
    print(tags)
    result = ["aaa", "bbb", "ccc", "xxx", "yyy"]
    assert tags == result
    assert len(tags) >= len(result)


class TestBuku:
    def test_bukudb(self):
        db = buku.BukuDb(dbfile=config.dbfile)
        print(f"Testing: {config.dbfile=}")
        db.add_rec("https://example.com")
        # db.delete_rec(1)
