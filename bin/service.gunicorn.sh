#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )
export HOME=$DIR/gramps/usr/src/gramps
cd $HOME/src
$DIR/bin/wait-for-configure.sh
if [[ -f /var/snap/platform/current/CI_TEST ]]; then
  export REQUESTS_CA_BUNDLE=/var/snap/platform/current/syncloud.ca.crt
fi
exec $DIR/gramps/sbin/python ${DIR}/gramps/usr/local/bin/gunicorn -c $DIR/gramps/usr/src/gramps/gunicorn.conf.py gramps.asgi:application
