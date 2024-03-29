import logging
import os
from pathlib import Path

import aiosql
import pytest
from alembic import command
from alembic.config import Config
from twbm.db.dal import DAL
from twbm.environment import config

_log = logging.getLogger()
log_fmt = r"%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(format=log_fmt, level=config.log_level, datefmt=datefmt)
# _log.propagate = True
_ = None


@pytest.fixture()
def data():
    return {
        "checksum": "159ce0a29c234510ba09c3091e0b513b",
        "roots": {
            "bookmark_bar": {
                "children": [
                    {
                        "date_added": "13084680099000000",
                        "id": "6",
                        "name": "Voyager",
                        "type": "url",
                        "url": "http://voyagerlive.org/",
                    },
                    {
                        "children": [
                            {
                                "date_added": "13084680167000000",
                                "id": "8",
                                "name": "0",
                                "type": "url",
                                "url": "file:///.startpage/0/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "9",
                                "name": "1",
                                "type": "url",
                                "url": "file:///.startpage/1/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "10",
                                "name": "2",
                                "type": "url",
                                "url": "file:///.startpage/2/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "11",
                                "name": "3",
                                "type": "url",
                                "url": "file:///.startpage/3/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "12",
                                "name": "4",
                                "type": "url",
                                "url": "file:///.startpage/4/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "13",
                                "name": "5",
                                "type": "url",
                                "url": "file:///.startpage/5/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "14",
                                "name": "6",
                                "type": "url",
                                "url": "file:///.startpage/6/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "15",
                                "name": "7",
                                "type": "url",
                                "url": "file:///.startpage/7/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "16",
                                "name": "8",
                                "type": "url",
                                "url": "file:///.startpage/8/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "17",
                                "name": "9",
                                "type": "url",
                                "url": "file:///.startpage/9/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "18",
                                "name": "10",
                                "type": "url",
                                "url": "file:///.startpage/10/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "19",
                                "name": "11",
                                "type": "url",
                                "url": "file:///.startpage/11/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "20",
                                "name": "12",
                                "type": "url",
                                "url": "file:///.startpage/12/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "21",
                                "name": "13",
                                "type": "url",
                                "url": "file:///.startpage/13/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "22",
                                "name": "14",
                                "type": "url",
                                "url": "file:///.startpage/14/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "23",
                                "name": "15",
                                "type": "url",
                                "url": "file:///.startpage/15/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "24",
                                "name": "16",
                                "type": "url",
                                "url": "file:///.startpage/16/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "25",
                                "name": "17",
                                "type": "url",
                                "url": "file:///.startpage/17/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "26",
                                "name": "18",
                                "type": "url",
                                "url": "file:///.startpage/18/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "27",
                                "name": "19",
                                "type": "url",
                                "url": "file:///.startpage/19/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "28",
                                "name": "20",
                                "type": "url",
                                "url": "file:///.startpage/20/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "29",
                                "name": "21",
                                "type": "url",
                                "url": "file:///.startpage/21/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "30",
                                "name": "22",
                                "type": "url",
                                "url": "file:///.startpage/22/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "31",
                                "name": "23",
                                "type": "url",
                                "url": "file:///.startpage/23/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "32",
                                "name": "24",
                                "type": "url",
                                "url": "file:///.startpage/24/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "33",
                                "name": "25",
                                "type": "url",
                                "url": "file:///.startpage/25/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "34",
                                "name": "26",
                                "type": "url",
                                "url": "file:///.startpage/26/index.html",
                            },
                            {
                                "date_added": "13084680271000000",
                                "id": "35",
                                "name": "27",
                                "type": "url",
                                "url": "file:///.startpage/27/index.html",
                            },
                        ],
                        "date_added": "13149362306499266",
                        "date_modified": "0",
                        "id": "7",
                        "name": "SP",
                        "type": "folder",
                    },
                    {
                        "children": [
                            {
                                "date_added": "13084680637000000",
                                "id": "37",
                                "name": "Flash Install",
                                "type": "url",
                                "url": "apt://flashplugin-installer",
                            },
                            {
                                "date_added": "13084680669000000",
                                "id": "38",
                                "name": "Adblock Plus",
                                "type": "url",
                                "url": "https://addons.mozilla.org/fr/firefox/addon/adblock-plus/",
                            },
                            {
                                "date_added": "13084680688000000",
                                "id": "39",
                                "name": "SearchPreview #xxx #yyy",
                                "type": "url",
                                "url": "https://addons.mozilla.org/fr/firefox/addon/searchpreview/",
                            },
                            {
                                "date_added": "13084680713000000",
                                "id": "40",
                                "name": "Language Tools",
                                "type": "url",
                                "url": "https://addons.mozilla.org/fr/firefox/language-tools/",
                            },
                        ],
                        "date_added": "13149362306505611",
                        "date_modified": "0",
                        "id": "36",
                        "name": "F+",
                        "type": "folder",
                    },
                    {
                        "children": [
                            {
                                "children": [
                                    {
                                        "date_added": "13084680036000000",
                                        "id": "43",
                                        "name": "Ubuntu",
                                        "type": "url",
                                        "url": "http://www.ubuntu.com/",
                                    },
                                    {
                                        "date_added": "13084680036000000",
                                        "id": "44",
                                        "name": "Ubuntu Wiki (community-edited website)",
                                        "type": "url",
                                        "url": "http://wiki.ubuntu.com/",
                                    },
                                    {
                                        "date_added": "13084680036000000",
                                        "id": "45",
                                        "name": "Make a Support Request to the Ubuntu Community",
                                        "type": "url",
                                        "url": "https://answers.launchpad.net/ubuntu/+addquestion",
                                    },
                                    {
                                        "date_added": "13084680036000000",
                                        "id": "46",
                                        "name": "Debian (Ubuntu is based on Debian)",
                                        "type": "url",
                                        "url": "http://www.debian.org/",
                                    },
                                    {
                                        "date_added": "13084680036000000",
                                        "id": "47",
                                        "name": "Ubuntu One - The personal cloud that brings your digital life together",
                                        "type": "url",
                                        "url": "https://one.ubuntu.com/",
                                    },
                                ],
                                "date_added": "13149362306508801",
                                "date_modified": "0",
                                "id": "42",
                                "name": "Ubuntu and Free Software links",
                                "type": "folder",
                            },
                            {
                                "children": [
                                    {
                                        "date_added": "13084680036000000",
                                        "id": "49",
                                        "name": "Help and Tutorials",
                                        "type": "url",
                                        "url": "https://www.mozilla.org/en-US/firefox/help/",
                                    },
                                    {
                                        "date_added": "13084680036000000",
                                        "id": "50",
                                        "name": "Customize Firefox",
                                        "type": "url",
                                        "url": "https://www.mozilla.org/en-US/firefox/customize/",
                                    },
                                    {
                                        "date_added": "13084680036000000",
                                        "id": "51",
                                        "name": "Get Involved",
                                        "type": "url",
                                        "url": "https://www.mozilla.org/en-US/contribute/",
                                    },
                                    {
                                        "date_added": "13084680036000000",
                                        "id": "52",
                                        "name": "About Us",
                                        "type": "url",
                                        "url": "https://www.mozilla.org/en-US/about/",
                                    },
                                ],
                                "date_added": "13149362306510034",
                                "date_modified": "0",
                                "id": "48",
                                "name": "Mozilla Firefox",
                                "type": "folder",
                            },
                        ],
                        "date_added": "13149362306507580",
                        "date_modified": "13149362306507581",
                        "id": "41",
                        "name": "Imported From Firefox",
                        "type": "folder",
                    },
                ],
                "date_added": "13149362288728239",
                "date_modified": "0",
                "id": "1",
                "name": "Bookmarks bar",
                "type": "folder",
            },
            "other": {
                "children": [
                    {
                        "date_added": "13149416292911928",
                        "id": "55",
                        "name": "Google",
                        "type": "url",
                        "url": "https://www.google.com/",
                    }
                ],
                "date_added": "13149362288728244",
                "date_modified": "13149416292911928",
                "id": "2",
                "name": "Other bookmarks",
                "type": "folder",
            },
            "synced": {
                "children": [],
                "date_added": "13149362288728244",
                "date_modified": "0",
                "id": "3",
                "name": "Mobile bookmarks",
                "type": "folder",
            },
        },
        "version": 1,
    }


# @pytest.fixture()
# def init_db():
#     p = Path(__file__).parent / 'tests_data'
#     shutil.copy(p / 'bm_fts.db.bkp', p / 'bm_fts.db')
#     print(f"Copying tests database")


@pytest.fixture()
def init_db():
    # TWBM_DB_URL=sqlite:///tests/tests_data/bm_test.db
    dsn = os.environ.get("TWBM_DB_URL", "sqlite:///tests/tests_data/bm_test.db")
    (Path(__file__).parent / "tests_data/bm_test.db").unlink(missing_ok=True)
    alembic_root = Path(__file__).parent.parent / "twbm/db"

    alembic_cfg = Config(alembic_root / "alembic.ini")
    alembic_cfg.set_main_option("script_location", str(alembic_root / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", dsn)

    command.upgrade(alembic_cfg, "head")
    _ = None


@pytest.fixture()
def dal(init_db):
    dal = DAL(env_config=config)
    with dal as dal:
        sql_files_path = Path(__file__).parent.absolute() / "sql"
        aiosql_queries = aiosql.from_path(f"{sql_files_path}", "sqlite3")
        aiosql_queries.load_testdata(dal.conn.connection)
        dal.conn.connection.commit()
        yield dal
