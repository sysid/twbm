#!/usr/bin/env bash
export LOG_LEVEL=DEBUG
export TWBM_DB_URL=sqlite:///sql/bm.db
#TWBM_DB_URL=sqlite:///test/tests_data/bm_test.db


test-pipe-update () {
  cp ~/vimwiki/buku/bm.db $PROJ_DIR/sql/bm.db
  python ./twbm/twb.py search --np xxxxx
  echo 1 2 | python ./twbm/twb.py update -t x
  python ./twbm/twb.py search --np xxxxx
  python ./twbm/twb.py search --np reconciling
}


################################################################################
#main
################################################################################
pushd $PROJ_DIR || exit
echo "-M- Using: $TWBM_DB_URL"
test-pipe-update
popd || exit
