#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )
$DIR/bin/wait-for-configure.sh
export REQUESTS_CA_BUNDLE=/var/snap/platform/current/syncloud.ca.crt
. "${SNAP_DATA}/config/env"
exec $DIR/gramps/sbin/python \
  ${DIR}/gramps/venv/bin/gunicorn \
  -w 4 \
  -b unix:/var/snap/gramps/common/web.socket \
  gramps_webapi.wsgi:app \
  --timeout 120 \
  --limit-request-line 8190
