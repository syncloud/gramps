#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )
$DIR/bin/wait-for-configure.sh
. "${SNAP_DATA}/config/env"
ls -1 /var/snap/gramps/current/gramps/grampsdb
exec $DIR/gramps/sbin/python \
  ${DIR}/gramps/usr/local/bin/celery \
  -A gramps_webapi.celery \
  worker \
  --loglevel=INFO \
  --concurrency=2
