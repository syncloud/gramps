import sys
from os.path import dirname, join
from syncloudlib.integration.conftest import *

DIR = dirname(__file__)
sys.path.insert(0, DIR)


@pytest.fixture(scope="session")
def project_dir():
    return join(DIR, '..')
