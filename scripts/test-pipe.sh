#!/usr/bin/env bash
export LOG_LEVEL=DEBUG
export TWBM_DB_URL=sqlite:///sql/bm.db
#TWBM_DB_URL=sqlite:///test/tests_data/bm_test.db

init-db () {
  cp ~/vimwiki/buku/bm.db $PROJ_DIR/sql/bm.db
}


test-pipe-update () {
  echo "-M- ------------------------------ ${FUNCNAME[0]} ------------------------------"
  init-db
  echo "-M- should not have tag: x"
  python ./twbm/twb.py search --np xxxxx
  echo 1 2 | python ./twbm/twb.py update -t x
  echo "-M- should have tag: x"
  python ./twbm/twb.py search --np xxxxx
}

test-pipe-update-interactive () {
  echo "-M- ------------------------------ ${FUNCNAME[0]} ------------------------------"
  init-db
  echo "-M- should not have tag: x"
  python ./twbm/twb.py search xxxxx | python ./twbm/twb.py update -t x
  echo "-M- should have tag: x"
  python ./twbm/twb.py search --np xxxxx
}


################################################################################
#main
################################################################################
echo "-M- Using: $TWBM_DB_URL"

pushd $PROJ_DIR || exit

#test-pipe-update
test-pipe-update-interactive

popd || exit
