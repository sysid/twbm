#!/usr/bin/env bash
BUKU_DB="$2"
TWBM_DB="$1"

_RESET="\e[0m"
_RED="\e[91m"
_GREEN="\e[92m"

Red() {
  printf "${_RED}%s${_RESET}\n" "$@"
}
Green() {
  printf "${_GREEN}%s${_RESET}\n" "$@"
}

usage() {
  cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") twbm_db buku_db

Downgrade from twbm database to buku database.
EOF
  exit
}

if [ -z "$TWBM_DB" ] || [ -z "$BUKU_DB" ]; then
  usage
fi

if [ ! -f "$TWBM_DB" ]; then
  Red "-E- $TWBM_DB does not exist."
  exit 1
fi
if [ -f "$BUKU_DB" ]; then
  Red "-E- $BUKU_DB does already exist, please remove to proceed."
  exit 1
fi

downgrade_buku_db() {
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

################################################################################
# main
################################################################################
downgrade_buku_db

echo "-M- Created $BUKU_DB with downgraded schema"
