#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
BUILD_DIR=${DIR}/../build/snap/gramps
mkdir -p ${BUILD_DIR}

PYTHON=/venv/bin/python3
BUILD_DEPS="build-essential python3-dev libldap-dev libsasl2-dev"

apt update
apt install -y --no-install-recommends ${BUILD_DEPS}
${PYTHON} -m pip install --no-cache-dir python-ldap==3.4.5
apt purge -y ${BUILD_DEPS}
apt autoremove -y
apt clean

SITE_PACKAGES=$(${PYTHON} -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')
WEBAPI=${SITE_PACKAGES}/gramps_webapi

cp ${DIR}/ldap_auth.py ${WEBAPI}/auth/ldap_auth.py
sed -i 's#^from .passwords import hash_password, verify_password#&\nfrom .ldap_auth import ldap_login#' ${WEBAPI}/auth/__init__.py
sed -i 's#^    """Return true if the user can be authenticated."""#&\n    if ldap_login(username, password):\n        return True#' ${WEBAPI}/auth/__init__.py
sed -i 's#^    """Return the authentication status for a username/password pair."""#&\n    if ldap_login(username, password):\n        return AUTH_STATUS_OK#' ${WEBAPI}/auth/__init__.py
test $(grep -c ldap_login ${WEBAPI}/auth/__init__.py) -eq 3

for main in /app/src/gramps_webapi/__main__.py ${WEBAPI}/__main__.py; do
  sed -i 's#sys\.executable#"/snap/gramps/current/gramps/sbin/python"#g' ${main}
  grep -q '/snap/gramps/current/gramps/sbin/python' ${main}
done
sed -i 's#if get_all_user_details(#if True or get_all_user_details(#g' ${WEBAPI}/api/resources/token.py
test $(grep -c 'if True or get_all_user_details(' ${WEBAPI}/api/resources/token.py) -eq 2
sed -i 's#<dir>/usr/share/fonts</dir>#<dir>/snap/gramps/current/gramps/usr/share/fonts</dir>#g' /etc/fonts/fonts.conf

rm -rf /usr/lib/*-linux-gnu*/dri

cp -a /bin ${BUILD_DIR}
cp -a /lib ${BUILD_DIR}
cp -r /usr ${BUILD_DIR}
cp -r /app ${BUILD_DIR}
cp -r /etc ${BUILD_DIR}
cp -r /venv ${BUILD_DIR}
cp --remove-destination -R ${DIR}/bin ${BUILD_DIR}/sbin
