#!/bin/bash -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )
ls -1 /var/snap/gramps/current/gramps/grampsdb | logger -t gramps
. "${SNAP_DATA}/config/env"
cd $DIR/gramps/app/src
$DIR/gramps/sbin/python \
  -m gramps_webapi \
  --config /var/snap/gramps/current/config/gramps.cfg \
  user migrate
ls -1 /var/snap/gramps/current/gramps/grampsdb | logger -t gramps
