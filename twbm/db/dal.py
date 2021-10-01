import logging
from datetime import datetime
from typing import Sequence, Optional

import aiosql
import sqlalchemy as sa
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, Connection

# from twbm.environment import Environment

_log = logging.getLogger(__name__)
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)
# logging.getLogger('sqlalchemy').setLevel(logging.DEBUG)

metadata = sa.MetaData()

sim_results_table = sa.Table(
    "bookmarks",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("URL", sa.String(), nullable=False, unique=True),
    sa.Column("metadata", sa.String(), default=""),
    sa.Column("tags", sa.String(), default=""),
    sa.Column("desc", sa.String(), default=""),
    sa.Column("flags", sa.Integer(), default=0),
    sa.Column(
        "last_update_ts", sa.DateTime(), server_default=sa.func.current_timestamp()
    ),
)


class Bookmark(BaseModel):
    id: int = None
    URL: str = ""
    metadata: Optional[str] = ""
    tags: str = ",,"
    desc: str = ""
    flags: int = 0
    last_update_ts: datetime = datetime.utcnow()

    @property
    def split_tags(self) -> Sequence[str]:
        return [tag for tag in self.tags.split(",") if tag != ""]


# noinspection PyPropertyAccess
class DAL:
    _sql_alchemy_db_engine: Engine
    _conn: Connection

    is_simulated_environment: bool

    def __init__(self, env_config: "Environment"):
        self.bm_db_url = env_config.twbm_db_url
        self.record_classes = {
            "Bookmark": Bookmark,
        }

        # aiosql setup
        # sql_files_path = Path(__file__).parent.absolute() / Path("sql")
        # self.aiosql_queries = aiosql.from_path(
        #     f"{sql_files_path}", "sqlite3", record_classes=record_classes
        # )
        # self.aiosql_queries = aiosql.from_path(f"{sql_files_path}", "sqlite3")

    def __enter__(self):
        self._sql_alchemy_db_engine: Engine = create_engine(self.bm_db_url)
        self._conn = self._sql_alchemy_db_engine.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._conn.close()
        self._sql_alchemy_db_engine.dispose()

    @property
    def conn(self):
        return self._conn

    # TODO: not working
    def delete_bookmark(self, id: int) -> int:
        query = """
            -- name: delete_bookmark<!
            delete from bookmarks where id = :id
            returning *;
        """
        queries = aiosql.from_str(query, "sqlite3")
        result = queries.delete_bookmark(self.conn.connection, id=id)
        self.conn.connection.commit()
        return result

    def insert_bookmark(self, bm: Bookmark) -> int:
        query = """
            -- name: insert_bookmark<!
            -- record_class: Bookmark
            insert into bookmarks (URL, metadata, tags, desc, flags)
            values (:URL, :metadata, :tags, :desc, :flags)
            returning *;
        """
        queries = aiosql.from_str(query, "sqlite3", record_classes=self.record_classes)
        result = queries.insert_bookmark(
            self.conn.connection,
            URL=bm.URL,
            metadata=bm.metadata,
            tags=bm.tags,
            desc=bm.desc,
            flags=bm.flags,
        )
        self.conn.connection.commit()
        return result

    def update_bookmark(self, bm: Bookmark) -> int:
        query = """
            -- name: update_bookmark<!
            update bookmarks
            set tags = :tags
            where id = :id
            returning *;
        """
        queries = aiosql.from_str(query, "sqlite3")
        result = queries.update_bookmark(self.conn.connection, id=bm.id, tags=bm.tags)
        self.conn.connection.commit()
        return result

    def get_bookmark_by_id(self, id_: int) -> Bookmark:
        # Example query
        # noinspection SqlResolve
        query = """
            -- name: get_bookmark_by_id^
            -- record_class: Bookmark
            select *
            from bookmarks
            where id = :id;
            """
        queries = aiosql.from_str(query, "sqlite3", record_classes=self.record_classes)
        sql_result = queries.get_bookmark_by_id(self.conn.connection, id=id_)
        if not sql_result:
            # noinspection PyRedundantParentheses
            return Bookmark()
        return sql_result

    def get_bookmarks(self, fts_query: str) -> Sequence[Bookmark]:
        # Example query
        # noinspection SqlResolve
        if fts_query != "":
            query = """
                -- name: get_bookmarks
                -- record_class: Bookmark
                select *
                from bookmarks_fts
                where bookmarks_fts match :fts_query
                order by rank;
            """
            queries = aiosql.from_str(
                query, "sqlite3", record_classes=self.record_classes
            )
            sql_result = queries.get_bookmarks(
                self.conn.connection, fts_query=fts_query
            )
        else:  # TODO: make normal query
            query = """
                -- name: get_bookmarks
                -- record_class: Bookmark
                select *
                from bookmarks_fts
                order by rank;
            """
            queries = aiosql.from_str(
                query, "sqlite3", record_classes=self.record_classes
            )
            sql_result = queries.get_bookmarks(
                self.conn.connection, fts_query=fts_query
            )

        if not sql_result:
            # noinspection PyRedundantParentheses
            return (Bookmark(),)
        return sql_result

    def get_related_tags(self, tag: str):
        tag_query = f"%,{tag},%"
        # noinspection SqlResolve
        query = """
            -- name: get_related_tags
            with RECURSIVE split(tags, rest) AS (
                SELECT '', tags || ','
                FROM bookmarks
                WHERE tags LIKE :tag_query
                -- WHERE tags LIKE '%,ccc,%'
                UNION ALL
                SELECT substr(rest, 0, instr(rest, ',')),
                       substr(rest, instr(rest, ',') + 1)
                FROM split
                WHERE rest <> '')
            SELECT tags, count(tags) as n
            FROM split
            WHERE tags <> ''
            group by tags
            ORDER BY 2 desc;
        """
        queries = aiosql.from_str(query, "sqlite3")
        sql_result = queries.get_related_tags(self.conn.connection, tag_query=tag_query)

        # if not sql_result:
        #     # noinspection PyRedundantParentheses
        #     return (Bookmark(),)
        return sql_result

    def get_all_tags(self, with_frequency: bool = False):
        # noinspection SqlResolve
        query = """
            -- name: get_all_tags
            with RECURSIVE split(tags, rest) AS (
                SELECT '', tags || ','
                FROM bookmarks
                UNION ALL
                SELECT substr(rest, 0, instr(rest, ',')),
                       substr(rest, instr(rest, ',') + 1)
                FROM split
                WHERE rest <> '')
            SELECT tags, count(tags) as n
            FROM split
            WHERE tags <> ''
            group by tags
            ORDER BY 2 desc;
        """
        queries = aiosql.from_str(query, "sqlite3")
        sql_result = queries.get_all_tags(self.conn.connection)

        return sql_result
        # if with_frequency:
        #     return sql_result
        # else:
        #     return [tags[0] for tags in sql_result]
