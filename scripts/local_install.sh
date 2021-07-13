#!/usr/bin/env bash

pushd $PROJ_DIR || exit 1
pipx uninstall twbm
make clean
make build
pipx install ~/dev/py/twbm
popd