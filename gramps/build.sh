#!/bin/bash -ex

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}
BUILD_DIR=${DIR}/../build/snap/gramps
mkdir -p ${BUILD_DIR}

apt update
apt install -y libldap2-dev libsasl2-dev
python3 -m pip install --break-system-packages --no-cache-dir python-ldap==3.4.0

mkdir tmp
cd tmp
wget -c --progress=dot:giga https://github.com/cyberb/gramps-web-api/archive/refs/heads/master.zip
unzip master.zip
cp gramps-web-api-master/gramps_webapi/auth/__init__.py /usr/local/lib/python3.11/dist-packages/gramps_webapi/auth
cd ..
rm -rf tmp

sed -i 's#sys\.executable#"/snap/gramps/current/gramps/sbin/python"#g' /app/src/gramps_webapi/__main__.py
sed -i 's#if get_all_user_details(#if True or get_all_user_details(#g' /usr/local/lib/python3.11/dist-packages/gramps_webapi/api/resources/token.py
#sed -i 's#dbid = "bsddb"#dbid = "sqlite"#g' /usr/local/lib/python3.11/dist-packages/gramps/gen/db/utils.py

cp -r /bin ${BUILD_DIR}
cp -r /usr ${BUILD_DIR}
cp -r /lib ${BUILD_DIR}
cp -r /app ${BUILD_DIR}
cp -r /etc ${BUILD_DIR}
cp --remove-destination -R ${DIR}/bin ${BUILD_DIR}/sbin
