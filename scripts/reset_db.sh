#!/usr/bin/env bash

#rm bm.db
#alembic upgrade head
#sqlite3 bm.db < original.bkp.sql

export_csv () {
sqlite3 sql/bm.db <<____HERE
.headers on
.mode csv
.once sql/buku_bm.csv
select id, URL, metadata, tags, desc, flags from bookmarks;
____HERE
}

BUKU_DB='sql/buku.db'
TWBM_DB='sql/bm.db'

downgrade_buku_db () {
sqlite3 "$BUKU_DB" <<____HERE
CREATE TABLE bookmarks (
        id INTEGER NOT NULL,
        "URL" VARCHAR NOT NULL,
        metadata VARCHAR,
        tags VARCHAR,
        "desc" VARCHAR,
        flags INTEGER,
        PRIMARY KEY (id),
        UNIQUE ("URL")
);

attach "$TWBM_DB" as bm;
.databases

insert into main.bookmarks (id, URL, metadata, tags, desc, flags)
select id, URL, metadata, tags, desc, flags
from bm.bookmarks;
select count(*) from main.bookmarks;
____HERE
}


pushd $PROJ_DIR || exit 1
#export_csv
downgrade_buku_db
popd

