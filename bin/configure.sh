#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )
export HOME=$DIR/gramps/usr/src/gramps
cd $HOME/src
export PATH=$DIR/gramps/sbin:$PATH
$DIR/gramps/sbin/python3 -m gramps_webapi --config /snap/var/gramps/current/config/config.cfg user migrate
