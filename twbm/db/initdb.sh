#!/usr/bin/env bash

rm bm.db
alembic upgrade head
sqlite3 bm.db < original.bkp.sql
