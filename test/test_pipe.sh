#!/usr/bin/env bash
RUN_ENV=testing


test-pipe-update () {
  cp ./tests/tests_data/bm_fts.db.bkp ./tests/tests_data/bm_fts.db
  python ./bookmark/twb.py search --np xxxxx
  echo 1 2 | python ./bookmark/twb.py update -t x
  python ./bookmark/twb.py search --np xxxxx
  python ./bookmark/twb.py search --np reconciling
}


################################################################################
#main
################################################################################
pushd $PROJ_DIR || exit
test-pipe-update
popd || exit
