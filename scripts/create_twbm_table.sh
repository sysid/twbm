CREATE TABLE alembic_version (
        version_num VARCHAR(32) NOT NULL,
        CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
CREATE TABLE bookmarks (
        id INTEGER NOT NULL,
        "URL" VARCHAR NOT NULL,
        metadata VARCHAR,
        tags VARCHAR,
        "desc" VARCHAR,
        flags INTEGER,
        last_update_ts DATETIME DEFAULT (CURRENT_TIMESTAMP),
        PRIMARY KEY (id),
        UNIQUE ("URL")
);
CREATE VIRTUAL TABLE bookmarks_fts USING fts5(
    id,
    URL,
    metadata,
    tags UNINDEXED,
    "desc",
    flags UNINDEXED,
    content='bookmarks',
    content_rowid='id',
    tokenize="porter unicode61",
)
/* bookmarks_fts(id,URL,metadata,tags,"desc",flags) */;
CREATE TABLE IF NOT EXISTS 'bookmarks_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE IF NOT EXISTS 'bookmarks_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS 'bookmarks_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE IF NOT EXISTS 'bookmarks_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE TRIGGER bookmarks_ai AFTER INSERT ON bookmarks
    BEGIN
        INSERT INTO bookmarks_fts (rowid, URL, metadata, "desc")
        VALUES (new.id, new.URL, new.metadata, new.desc);
    END;
CREATE TRIGGER bookmarks_ad AFTER DELETE ON bookmarks
    BEGIN
        INSERT INTO bookmarks_fts (bookmarks_fts, rowid, URL, metadata, "desc")
        VALUES ('delete', old.id, old.URL, old.metadata, old.desc);
    END;
CREATE TRIGGER bookmarks_au AFTER UPDATE ON bookmarks
    BEGIN
        INSERT INTO bookmarks_fts (bookmarks_fts, rowid, URL, metadata, "desc")
        VALUES ('delete', old.id, old.URL, old.metadata, old.desc);
        INSERT INTO bookmarks_fts (rowid, URL, metadata, "desc")
        VALUES (new.id, new.URL, new.metadata, new.desc);
    END;
CREATE TRIGGER [UpdateLastTime] AFTER UPDATE ON bookmarks
    FOR EACH ROW WHEN NEW.last_update_ts <= OLD.last_update_ts
    BEGIN
        update bookmarks set last_update_ts=CURRENT_TIMESTAMP where id=OLD.id;
    END;