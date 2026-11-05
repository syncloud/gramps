#!/bin/sh -ex

DIR=$( cd "$( dirname "$0" )" && pwd )
cd ${DIR}

BUILD_DIR=${DIR}/../build/snap/gramps
$BUILD_DIR/sbin/python --version
$BUILD_DIR/sbin/python ${BUILD_DIR}/venv/bin/celery --version
$BUILD_DIR/sbin/tesseract --list-langs | grep eng
$BUILD_DIR/sbin/tesseract --list-langs | tail
$BUILD_DIR/sbin/tesseract --version
$BUILD_DIR/sbin/python -c 'from gi.repository import GLib'
$BUILD_DIR/sbin/python -c 'import ldap, gramps_webapi.auth, gramps_webapi.app, gramps.gen.const'
$BUILD_DIR/sbin/python ${BUILD_DIR}/venv/bin/gunicorn --version
$BUILD_DIR/sbin/pdftotext -v
$BUILD_DIR/sbin/gpg --version | head -1
