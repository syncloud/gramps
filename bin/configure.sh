#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )
cd $DIR/gramps/app/src
$DIR/gramps/sbin/python \
  -m gramps_webapi \
  --config /var/snap/gramps/current/config/gramps.cfg \
  user migrate
