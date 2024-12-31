#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )
export HOME=$DIR/gramps/usr/src/gramps
cd $HOME/src
export PATH=$DIR/gramps/sbin:$PATH
$DIR/bin/wait-for-configure.sh
exec $DIR/gramps/sbin/python ${DIR}/gramps/usr/local/bin/celery -A gramps_webapi.celery worker --loglevel=INFO --concurrency=2
