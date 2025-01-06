#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )
$DIR/bin/wait-for-configure.sh
export GRAMPS_API_CONFIG=/var/snap/gramps/current/config/gramps.cfg
exec $DIR/gramps/sbin/python \
  ${DIR}/gramps/usr/local/bin/celery \
  -A gramps_webapi.celery \
  worker \
  --loglevel=INFO \
  --concurrency=2
