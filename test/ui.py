import pytest
from os.path import dirname, join
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

    elem = selenium.find_by(By.CSS_SELECTOR, "gramps-js").shadow_root
    elem = selenium.find_by(By.CSS_SELECTOR, "grampsjs-main-menu", elem).shadow_root
    elem = selenium.find_by(By.CSS_SELECTOR, "mwc-list grampsjs-list-item", elem)
    assert elem.text == "Home Page"

    # home = selenium.driver.execute_script(
    #     'return     document'
    #     '.querySelector("gramps-js").shadowRoot'
    #     '.querySelector("grampsjs-main-menu").shadowRoot'
    #     '.querySelector("mwc-list grampsjs-list-item span")'
    # )

    selenium.screenshot('main')
