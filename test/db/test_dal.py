import os

import pytest

os.environ[
    "RUN_ENV"
] = "testing"  # Gotcha: make sure environment setup is before app is sourced
from db.dal import DAL, metadata, Bookmark
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
    results = dal.get_bookmarks(fts_query="security")
    # for result in results:
    #     print(f"{result.use_case}, {result.reason}, {result.strategy}")
    assert len(results) > 0
    assert isinstance(results[0], Bookmark)


def test_get_bookmarks_via_fts(dal):
    bms = dal.get_bookmarks(fts_query="security")
    assert len(bms) == 36


def test_get_bookmarks_raw(dal):
    bms = dal.get_bookmarks(fts_query="")
    assert len(bms) >= 1000


def test_get_xxxxx(dal):
    # this is the testing entry in bm.db
    bms = dal.get_bookmarks(fts_query="xxxxx")
    assert len(bms) == 1
    assert bms[0].tags == ',knowhow,ob,sec,'


def test_update_bm(dal):
    bm = dal.get_bookmarks(fts_query="xxxxx")[0]
    assert bm.tags == ',knowhow,ob,sec,'

    bm.tags = ',xxx,'
    result = dal.update_bookmark(bm)

    assert dal.get_bookmarks(fts_query="xxxxx")[0].tags == ',xxx,'


def test_insert_bm(dal):
    bm = Bookmark(
        URL="http://aaaaa/bbbbb",
        metadata="metadata",
        tags=",aaa,bbb,",
        desc="description",
        flags=0,
    )
    result = dal.insert_bookmark(bm)

    assert dal.get_bookmarks(fts_query="aaaaa")[0].tags == ',aaa,bbb,'


# TODO: not working
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
    assert '' not in tags


def test_get_related_tags(dal):
    tags = dal.get_related_tags(tag='py')
    print(tags)
    _ = None
