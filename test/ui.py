import time

import pytest
from os.path import dirname, join

from retry import retry
from selenium.webdriver.common.by import By
from subprocess import check_output
from syncloudlib.integration.hosts import add_host_alias

DIR = dirname(__file__)
TMP_DIR = '/tmp/syncloud/ui'


@pytest.fixture(scope="session")
def module_setup(request, device, artifact_dir, ui_mode, driver, selenium):
    def teardown():
        device.activated()
        device.run_ssh('mkdir -p {0}'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl > {0}/journalctl.ui.{1}.log'.format(TMP_DIR, ui_mode), throw=False)
        device.run_ssh('cat /var/snap/platform/current/config/authelia/config.yml > {0}/authelia.config.ui.log'.format(TMP_DIR), throw=False)
        device.scp_from_device('{0}/*'.format(TMP_DIR), join(artifact_dir, 'log'))
        check_output('cp /videos/* {0}'.format(artifact_dir), shell=True)
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)
        selenium.log()

    request.addfinalizer(teardown)


def test_start(module_setup, app, domain, device_host):
    add_host_alias(app, device_host, domain)


def test_login(selenium, device_user, device_password):
    selenium.open_app()
    selenium.find_by(By.ID, "username").send_keys(device_user)
    password = selenium.find_by(By.ID, "password")
    password.send_keys(device_password)
    selenium.screenshot('login')
    selenium.driver.execute_script(
        'return document'
        '.querySelector("gramps-js").shadowRoot'
        '.querySelector("grampsjs-login").shadowRoot'
        '.querySelector("mwc-button")'
    ).click()

    @retry(exceptions=Exception, tries=10, delay=1, backoff=2)
    def get_home():
        return selenium.driver.execute_script(
            'return     document'
            '.querySelector("gramps-js").shadowRoot'
            '.querySelector("grampsjs-main-menu").shadowRoot'
            '.querySelector("mwc-list grampsjs-list-item span")'
        )
    home = get_home()
    assert home.text == "Home Page"
    selenium.screenshot('main')


def test_add_person(selenium):
    selenium.driver.execute_script(
        'return document'
        '.querySelector("gramps-js").shadowRoot'
        '.querySelector("grampsjs-app-bar").shadowRoot'
        '.querySelector("grampsjs-add-menu").shadowRoot'
        '.querySelector("mwc-icon-button").shadowRoot'
        '.querySelector("button")'
    ).click()
    selenium.screenshot('add-person-1')

    @retry(exceptions=Exception, tries=10, delay=1, backoff=2)
    def get_button():
        return selenium.driver.execute_script(
            'return document'
            '.querySelector("gramps-js").shadowRoot'
            '.querySelector("grampsjs-app-bar").shadowRoot'
            '.querySelector("grampsjs-add-menu").shadowRoot'
            '.querySelector("mwc-menu grampsjs-list-item[href=\'/new_person\'] span")'
        )
    btn = get_button()
    btn.click()

    @retry(exceptions=Exception, tries=10, delay=1, backoff=2)
    def get_header():
        return selenium.driver.execute_script(
            'return     document'
            '.querySelector("gramps-js").shadowRoot'
            '.querySelector("grampsjs-pages").shadowRoot'
            '.querySelector("grampsjs-view-new-person").shadowRoot'
            '.querySelector("h2")'
        )
    header = get_header()
    assert header.text == "New Person"

    selenium.screenshot('add-person-2')

