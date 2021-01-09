#!/usr/bin/env bash
set +ex
source ~/dev/binx/profile/sane_bash.sh

TWBASH_DEBUG=true
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
START_TIME=$SECONDS

echo "-M- Start $(date)"

twpushd ../twbm || exit 1
[ -f buku ] && rm buku
wget https://raw.githubusercontent.com/jarun/buku/master/buku ./buku
diff buku.py buku
twpopd

echo "-M- End: $(($SECONDS - $START_TIME))"
exit 0
