#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )
$DIR/bin/wait-for-configure.sh
if [[ -f /var/snap/platform/current/CI_TEST ]]; then
  export REQUESTS_CA_BUNDLE=/var/snap/platform/current/syncloud.ca.crt
fi
export GRAMPS_API_CONFIG=/var/snap/gramps/current/config/gramps.cfg
exec $DIR/gramps/sbin/python \
  ${DIR}/gramps/usr/local/bin/gunicorn \
  -w 8 \
  -b unix:/var/snap/gramps/common/web.socket \
  gramps_webapi.wsgi:app \
  --timeout 120 \
  --limit-request-line 8190
