import json
import os
from os.path import join
from subprocess import check_output

import pytest
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from syncloudlib.http import wait_for_rest
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.installer import local_install

import snapd
from gramps_api import GrampsApi

TMP_DIR = '/tmp/syncloud'
SERVICES = ['redis', 'gunicorn', 'celery']

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


@pytest.fixture(scope="session")
def module_setup(request, device, app_dir, artifact_dir):
    def module_teardown():
        device.run_ssh('mkdir -p {0}'.format(TMP_DIR), throw=False)
        device.run_ssh('ls -la /var/snap/gramps/current/config > {0}/config.ls.log'.format(TMP_DIR), throw=False)
        device.run_ssh('top -bn 1 -w 500 -c > {0}/top.log'.format(TMP_DIR), throw=False)
        device.run_ssh('ps auxfw > {0}/ps.log'.format(TMP_DIR), throw=False)
        device.run_ssh('netstat -nlp > {0}/netstat.log'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl | tail -1000 > {0}/journalctl.log'.format(TMP_DIR), throw=False)
        device.run_ssh('ls -la /snap/gramps > {0}/snap.ls.log'.format(TMP_DIR), throw=False)
        device.run_ssh('ls -la /var/snap/gramps/current/ > {0}/var.snap.current.ls.log'.format(TMP_DIR), throw=False)
        device.run_ssh('ls -la /var/snap/gramps/common > {0}/var.snap.common.ls.log'.format(TMP_DIR), throw=False)
        device.run_ssh('ls -la /data/gramps > {0}/data.ls.log'.format(TMP_DIR), throw=False)
        device.run_ssh('cat /etc/hosts > {0}/hosts.log'.format(TMP_DIR), throw=False)
        device.run_ssh('ls -la /var/snap/gramps/current/grampsdb > {0}/grampsdb.log'.format(TMP_DIR), throw=False)

        app_log_dir = join(artifact_dir, 'log')
        os.makedirs(app_log_dir, exist_ok=True)
        device.scp_from_device('{0}/*'.format(TMP_DIR), app_log_dir, throw=False)
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)

    request.addfinalizer(module_teardown)


@pytest.fixture(scope="session")
def api(app_domain, device_user, device_password):
    return GrampsApi(app_domain, device_user, device_password)


def assert_clean_start(device):
    for service in SERVICES:
        restarts = device.run_ssh('systemctl show -p NRestarts --value snap.gramps.{0}.service'.format(service))
        assert restarts.strip() == '0', service


def test_start(module_setup, device, device_host, app, domain):
    add_host_alias(app, device_host, domain)
    device.run_ssh('date', retries=100)
    device.run_ssh('mkdir -p {0}'.format(TMP_DIR))
    snapd.settle(device)


@pytest.mark.flaky(retries=50, delay=10)
def test_activate_device(device):
    response = device.activate_custom()
    assert response.status_code == 200, response.text


def test_ca_cert(device, app_domain):
    device.run_ssh('CURL_CA_BUNDLE=/var/snap/platform/current/syncloud.ca.crt curl -v https://{0} 2>&1 > {1}/ssl.ca.log'.format(app_domain, TMP_DIR))


def test_install(app_archive_path, device_host, device_password, device):
    device.run_ssh('touch /var/snap/platform/current/CI_TEST')
    local_install(device_host, device_password, app_archive_path)


def test_index(app_domain):
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 100)


def test_clean_start(device):
    assert_clean_start(device)


@pytest.mark.flaky(retries=10, delay=10)
def test_login(api):
    assert api.token()


def test_add_person(api):
    api.add_person('Backup', 'Person')
    assert api.people_count() == 1


def test_storage_change_event(device):
    device.run_ssh('snap run gramps.storage-change > {0}/storage-change.log'.format(TMP_DIR))


def test_access_change_event(device):
    device.run_ssh('snap run gramps.access-change > {0}/access-change.log'.format(TMP_DIR))


def test_backup_restore(device, artifact_dir, device_host, device_password, app_archive_path, app_domain, api):
    device.run_ssh("snap run platform.cli backup create gramps")
    response = device.run_ssh("snap run platform.cli backup list")
    open('{0}/cli.backup.list.json'.format(artifact_dir), 'w').write(response)
    backup = json.loads(response)[0]
    device.run_ssh('tar tvf {0}/{1}'.format(backup['path'], backup['file']))
    device.run_ssh("snap remove gramps")
    local_install(device_host, device_password, app_archive_path)
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 100)
    assert api.people_count() == 0

    device.run_ssh("snap run platform.cli backup restore {0}".format(backup['file']))
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 100)
    assert api.people_count() == 1


def test_remove(device, app):
    response = device.app_remove(app)
    assert response.status_code == 200, response.text


def test_reinstall(app_archive_path, device_host, device_password, app_domain, device):
    local_install(device_host, device_password, app_archive_path)
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 100)
    assert_clean_start(device)


def test_upgrade(app_archive_path, device_host, device_password, app_domain, device):
    local_install(device_host, device_password, app_archive_path)
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 100)
    assert_clean_start(device)


@pytest.mark.flaky(retries=3, delay=1)
def test_access_change(device):
    device.run_ssh("snap run gramps.access-change")
