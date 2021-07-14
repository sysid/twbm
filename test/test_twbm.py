import logging
import os
import sqlite3
from os.path import exists
from tempfile import TemporaryDirectory

import pytest
import yaml

# from twbm.load_db import BukuDb
from twbm.buku import BukuDb

_log = logging.getLogger(__name__)
# log_fmt = r'%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s'
# logging.basicConfig(format=log_fmt, level=logging.DEBUG)

tests_data_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "tests_data"
)

# TEST_TEMP_DIR_OBJ = TemporaryDirectory(prefix='bukutest_')
TEST_TEMP_DIR_OBJ = TemporaryDirectory(prefix="bukutest_")
# TEST_TEMP_DIR_PATH = TEST_TEMP_DIR_OBJ.name
TEST_TEMP_DIR_PATH = "/tmp/bukutest"
TEST_TEMP_DBDIR_PATH = os.path.join(TEST_TEMP_DIR_PATH, "buku")
TEST_TEMP_DBFILE_PATH = os.path.join(TEST_TEMP_DBDIR_PATH, "bookmarks.db")

"""
test for sort order:
cls; python ./twbm/buku.py --db bm.db --np -t 'bb + py' --deep -- test
"""


@pytest.fixture()
def setup():
    if exists(TEST_TEMP_DBFILE_PATH):
        _log.info(f"Removing {TEST_TEMP_DBDIR_PATH}")
        os.remove(TEST_TEMP_DBFILE_PATH)


@pytest.fixture()
def db(request, setup):
    _log.info("setup")

    db = BukuDb(dbfile=TEST_TEMP_DBFILE_PATH)

    def teardown():
        _log.info("teardown")

    request.addfinalizer(teardown)

    return db


class PrettySafeLoader(
    yaml.SafeLoader
):  # pylint: disable=too-many-ancestors,too-few-public-methods
    def construct_python_tuple(self, node):
        return tuple(self.construct_sequence(node))


PrettySafeLoader.add_constructor(
    "tag:yaml.org,2002:python/tuple", PrettySafeLoader.construct_python_tuple
)


@pytest.fixture()
def chrome_db():
    # compatibility
    dir_path = os.path.dirname(os.path.realpath(__file__))
    res_yaml_file = os.path.join(dir_path, "tests_data", "25491522_res.yaml")
    res_nopt_yaml_file = os.path.join(dir_path, "tests_data", "25491522_res_nopt.yaml")
    json_file = os.path.join(dir_path, "tests_data", "Bookmarks")
    return json_file, res_yaml_file, res_nopt_yaml_file


def test_initdb(setup):
    assert not exists(TEST_TEMP_DBFILE_PATH)
    conn, curr = BukuDb.initdb(dbfile=TEST_TEMP_DBFILE_PATH)
    assert isinstance(conn, sqlite3.Connection)
    assert isinstance(curr, sqlite3.Cursor)
    assert exists(TEST_TEMP_DBFILE_PATH)
    curr.close()
    conn.close()


class ChromeTests:
    @pytest.mark.parametrize("add_pt", [True])
    def test_load_chrome_database(self, chrome_db, db, add_pt):
        """test method."""
        # compatibility
        json_file = chrome_db[0]

        db.load_chrome_database(json_file, None, add_pt)
        _ = None

    @pytest.mark.parametrize("add_pt", [True, False])
    def test_load_chrome_database_mock(self, chrome_db, db, add_pt):
        """test method."""
        # compatibility
        json_file = chrome_db[0]

        # with parent-tags and without
        res_yaml_file = chrome_db[1] if add_pt else chrome_db[2]

        with open(res_yaml_file, "r") as f:
            try:
                res_yaml = yaml.load(f, Loader=yaml.FullLoader)
            except RuntimeError:
                res_yaml = yaml.load(f, Loader=PrettySafeLoader)

        # this results in NOT having DB entries!!!
        # db.add_rec = mock.Mock()
        db.load_chrome_database(json_file, None, add_pt)
        # call_args_list_dict = dict(db.add_rec.call_args_list)
        # assert call_args_list_dict == res_yaml
        _ = None

    def test_traverse_bm_folder(self, db, data):
        bookmark_bar = data["roots"]["bookmark_bar"]
        for item in db.traverse_bm_folder(
            bookmark_bar["children"],
            unique_tag=None,
            folder_name="Bookmarks bar",
            add_parent_folder_as_tag=True,
        ):
            if "SearchPreview" in item[1]:
                assert item[2] == ",bookmarks bar,f+,xxx,yyy,"
            print(item)
