import pytest

import logging
log = logging.getLogger(__name__)


from karakara.tests.data.queue import *
from karakara.tests.data.tracks import *
from karakara.tests.data.tracks_random import *
from karakara.tests.data.auth import *

# Markers ----------------------------------------------------------------------

def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", help="run slow tests")
    parser.addoption("--ini_file", action="store", default="test.ini", help="pyramid ini file profile")
def pytest_runtest_setup(item):
    if 'unimplemented' in item.keywords: #and not item.config.getoption("--runslow"):
        pytest.skip('unimplemented functionality')
    if 'unfinished' in item.keywords:
        pytest.skip('unfinished functionality')
    try:
        runslow = item.config.getoption("--runslow")
    except ValueError:
        runslow = False
    if 'slow' in item.keywords and not runslow:
        pytest.skip("need --runslow option to run")

    logging.basicConfig(level=logging.DEBUG)

unimplemented = pytest.mark.unimplemented # Server dose not support the functionlity this test is asserting yet
unfinished    = pytest.mark.unfinished    # The test is unfinished and currently is know to fail
xfail         = pytest.mark.xfail
slow          = pytest.mark.slow

# Fixtures ---------------------------------------------------------------------

@pytest.fixture(scope="session")
def ini_file(request):
    return request.config.getoption("--ini_file")
@pytest.fixture(scope="session")
def app_ini(request, ini_file):
    """
    Settings object derived from .ini file required to start Pyramid app
    """
    from pyramid.paster import get_appsettings
    return get_appsettings(ini_file)


@pytest.fixture(scope="session")
def app(request, app_ini, DBSession):
    """
    Start KaraKara application
    """
    from webtest import TestApp
    from karakara import main as karakara_main

    app = TestApp(karakara_main({}, **app_ini))

    def finalizer():
        #print('tearDown WebApp')
        pass
    request.addfinalizer(finalizer)

    return app


@pytest.fixture(scope="session")
def DBSession(request, app_ini):
    """
    Init/Clear database
    """

    from karakara.model import DBSession, init_DBSession, init_DBSession_tables, clear_DBSession_tables
    init_DBSession(app_ini)
    clear_DBSession_tables()
    init_DBSession_tables()

    return DBSession


@pytest.fixture(scope="session")
def commit(request, DBSession):
    """
    Save data attached to DBSession
    """
    from karakara.model import commit
    return commit


@pytest.fixture(scope="session")
def cache_store(request, app):
    return app.app.registry.settings['cache.store']


@pytest.fixture()
def registry_settings(request, app):
    """
    registry.settings dictionary used in the running KaraKara app
    can be used with
    with patch.dict(settings, {'key': 'value'}):
    """
    return app.app.registry.settings


@pytest.fixture(autouse=True)
def mock_send_websocket_message(mocker):
    return mocker.patch('karakara.websocket._send_websocket_message')
