#!/usr/bin/env bash

# rm bm.db
# alembic upgrade head
# sqlite3 bm.db < original.bkp.sql

cmd="cp ~/vimwiki/buku/bm.db $PROJ_DIR/sql/bm.db"
echo "$cmd"
eval $omd
