#!/usr/bin/env bash

LOG_LEVEL=DEBUG TWBM_DB_URL=sqlite:///sql/bm.db python twbm/twb.py add https://www.google.com -t py,pz --title Title