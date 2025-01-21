import json
from os.path import dirname, join
from subprocess import check_output

import pytest
import requests
from selenium.webdriver.common.by import By
from syncloudlib.http import wait_for_rest
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.installer import local_install

DIR = dirname(__file__)
TMP_DIR = '/tmp/syncloud/ui'


@pytest.fixture(scope="session")
def module_setup(request, device, artifact_dir, ui_mode, driver, selenium):
    def teardown():
        device.activated()
        device.run_ssh('mkdir -p {0}'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl > {0}/journalctl.ui.log'.format(TMP_DIR, ui_mode), throw=False)
        device.run_ssh('ls -la /var/snap/gramps/current/gramps/grampsdb > {0}/grampsdb.ui.log'.format(TMP_DIR), throw=False)
        device.run_ssh(
            'cat /var/snap/platform/current/config/authelia/config.yml > {0}/authelia.config.ui.log'.format(TMP_DIR),
            throw=False)
        device.scp_from_device('{0}/*'.format(TMP_DIR), join(artifact_dir, 'log'))
        check_output('cp /videos/* {0}'.format(artifact_dir), shell=True)
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)
        selenium.log()

    request.addfinalizer(teardown)


def test_start(module_setup, device, app, domain, device_host):
    add_host_alias(app, device_host, domain)
    device.activated()


def test_login(selenium, device_user, device_password):
    selenium.open_app()
    login(device_password, device_user, selenium)
    selenium.screenshot('main')


def test_add_person(selenium):
    selenium.element_by_js(
        'document'
        '.querySelector("gramps-js").shadowRoot'
        '.querySelector("grampsjs-app-bar").shadowRoot'
        '.querySelector("grampsjs-add-menu").shadowRoot'
        '.querySelector("mwc-icon-button").shadowRoot'
        '.querySelector("button")'
    ).click()
    selenium.screenshot('add-person-empty')

    selenium.element_by_js(
        'document'
        '.querySelector("gramps-js").shadowRoot'
        '.querySelector("grampsjs-app-bar").shadowRoot'
        '.querySelector("grampsjs-add-menu").shadowRoot'
        '.querySelector("mwc-menu grampsjs-list-item[href=\'/new_person\'] span")'
    ).click()

    header = selenium.element_by_js(
        'document'
        '.querySelector("gramps-js").shadowRoot'
        '.querySelector("grampsjs-pages").shadowRoot'
        '.querySelector("grampsjs-view-new-person").shadowRoot'
        '.querySelector("h2")'
    )
    assert header.text == "New Person"

    selenium.element_by_js(
        'document'
        '.querySelector("body > gramps-js").shadowRoot'
        '.querySelector("grampsjs-pages").shadowRoot'
        '.querySelector("grampsjs-view-new-person").shadowRoot'
        '.querySelector("#primary-name").shadowRoot'
        '.querySelector("#first_name").shadowRoot'
        '.querySelector("mwc-textfield").shadowRoot'
        '.querySelector("label > input")'
    ).send_keys("First Name 1")

    selenium.element_by_js(
        'document'
        '.querySelector("body > gramps-js").shadowRoot'
        '.querySelector("grampsjs-pages").shadowRoot'
        '.querySelector("grampsjs-view-new-person").shadowRoot'
        '.querySelector("#primary-name").shadowRoot'
        '.querySelector("#surnames0").shadowRoot'
        '.querySelector("#surname").shadowRoot'
        '.querySelector("mwc-textfield").shadowRoot'
        '.querySelector("label > input")'
    ).send_keys("Last Name 1")
    selenium.screenshot('add-person-before-save')

    save = selenium.element_by_js(
        'document'
        '.querySelector("body > gramps-js").shadowRoot'
        '.querySelector("grampsjs-pages").shadowRoot'
        '.querySelector("grampsjs-view-new-person").shadowRoot'
        '.querySelector("mwc-button[icon=save]").shadowRoot'
        '.querySelector("#button")'
    )
    save.click()

    name = selenium.element_by_js(
        'document'
        '.querySelector("body > gramps-js").shadowRoot'
        '.querySelector("grampsjs-pages").shadowRoot'
        '.querySelector("grampsjs-view-person").shadowRoot'
        '.querySelector("grampsjs-person").shadowRoot'
        '.querySelector("h2")'
    )
    assert name.text == "First Name 1 Last Name 1"

    selenium.screenshot('add-person-saved')


def test_backup(selenium, device, artifact_dir, device_host, device_user, device_password, app_archive_path, app_domain):
    device.run_ssh("snap run platform.cli backup create gramps")
    response = device.run_ssh("snap run platform.cli backup list")
    open('{0}/cli.backup.list.json'.format(artifact_dir), 'w').write(response)
    backup = json.loads(response)[0]
    device.run_ssh('tar tvf {0}/{1}'.format(backup['path'], backup['file']))
    device.run_ssh("snap remove gramps")
    local_install(device_host, device_password, app_archive_path)
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 10)

    selenium.open_app()
    login(device_password, device_user, selenium)
    assert stats(selenium).text == "0"

    device.run_ssh('ls -la /var/snap/gramps/current/gramps/grampsdb'), throw=False)
        
    device.run_ssh("snap run platform.cli backup restore {0}".format(backup['file']))
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 10)

    device.run_ssh('ls -la /var/snap/gramps/current/gramps/grampsdb', throw=False)
        
    selenium.open_app()
    login(device_password, device_user, selenium)
    assert stats(selenium).text == "1"

    selenium.screenshot('backup-restored')


def login(device_password, device_user, selenium):
    selenium.find_by(By.ID, "username").send_keys(device_user)
    password = selenium.find_by(By.ID, "password")
    password.send_keys(device_password)
    selenium.screenshot('login')
    selenium.element_by_js(
        'document'
        '.querySelector("gramps-js").shadowRoot'
        '.querySelector("grampsjs-login").shadowRoot'
        '.querySelector("mwc-button")'
    ).click()
    home = selenium.element_by_js(
        'document'
        '.querySelector("gramps-js").shadowRoot'
        '.querySelector("grampsjs-main-menu").shadowRoot'
        '.querySelector("mwc-list grampsjs-list-item span")'
    )
    assert home.text == "Home Page"


def stats(selenium):
    name = selenium.element_by_js(
        'document'
        '.querySelector("body > gramps-js").shadowRoot'
        '.querySelector("grampsjs-pages").shadowRoot'
        '.querySelector("grampsjs-view-dashboard").shadowRoot'
        '.querySelector("#statistics").shadowRoot'
        '.querySelector("table > tr:nth-child(1) > td")'
    )
    return name
