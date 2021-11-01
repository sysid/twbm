"""create all

Revision ID: 7c2eff0bf291
Revises: 
Create Date: 2021-07-04 08:58:51.947770

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7c2eff0bf291"
down_revision = None
branch_labels = None
depends_on = None

after_insert = """
CREATE TRIGGER bookmarks_ai AFTER INSERT ON bookmarks
    BEGIN
        INSERT INTO bookmarks_fts (rowid, URL, metadata, tags, "desc")
        VALUES (new.id, new.URL, new.metadata, new.tags, new.desc);
    END;
"""

# noinspection SqlResolve
after_delete = """
CREATE TRIGGER bookmarks_ad AFTER DELETE ON bookmarks
    BEGIN
        INSERT INTO bookmarks_fts (bookmarks_fts, rowid, URL, metadata, tags, "desc")
        VALUES ('delete', old.id, old.URL, old.metadata, old.tags, old.desc);
    END;
"""

# noinspection SqlResolve
after_update = """
CREATE TRIGGER bookmarks_au AFTER UPDATE ON bookmarks
    BEGIN
        INSERT INTO bookmarks_fts (bookmarks_fts, rowid, URL, metadata, tags, "desc")
        VALUES ('delete', old.id, old.URL, old.metadata, old.tags, old.desc);
        INSERT INTO bookmarks_fts (rowid, URL, metadata, tags, "desc")
        VALUES (new.id, new.URL, new.metadata, new.tags, new.desc);
    END;
"""

create_fts = """
CREATE VIRTUAL TABLE bookmarks_fts USING fts5(
    id,
    URL,
    metadata,
    tags,
    "desc",
    flags UNINDEXED,
    last_update_ts UNINDEXED,
    content='bookmarks',
    content_rowid='id',
    tokenize="porter unicode61",
);
"""

update_time_trigger = """
CREATE TRIGGER [UpdateLastTime] AFTER UPDATE ON bookmarks
    FOR EACH ROW WHEN NEW.last_update_ts <= OLD.last_update_ts
    BEGIN
        update bookmarks set last_update_ts=CURRENT_TIMESTAMP where id=OLD.id;
    END;
"""


def upgrade():
    op.create_table(
        "bookmarks",
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
    op.execute(create_fts)
    op.execute(after_insert)
    op.execute(after_delete)
    op.execute(after_update)
    op.execute(update_time_trigger)


def downgrade():
    op.drop_table("bookmarks")
