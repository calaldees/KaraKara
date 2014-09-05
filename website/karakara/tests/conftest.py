import pytest

import logging
log = logging.getLogger(__name__)

INI = 'test.ini'
#INI = 'production.ini'

from karakara.tests.data.tracks import *
from karakara.tests.data.tracks_random import *

# Markers ----------------------------------------------------------------------

def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", help="run slow tests")
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
def app_ini(request, ini_file=INI):
    from pyramid.paster import get_appsettings
    return get_appsettings(ini_file)


@pytest.fixture(scope="session")
def app(request, app_ini):
    from webtest import TestApp
    from karakara import main as karakara_main

    #print('setup WebApp')
    app = TestApp(karakara_main({}, **app_ini))

    from karakara.model.init_data import init_data
    init_data()

    def finalizer():
        #print('tearDown WebApp')
        pass
    request.addfinalizer(finalizer)

    return app


@pytest.fixture(scope="session")
def DBSession(request, app):
    """
    Aquire DBSession from WebTest App
    The WSGI app has already been started,
    we can import the session safly knowing it has been setup
    """
    from karakara.model import DBSession
    return DBSession


@pytest.fixture(scope="session")
def commit(request, DBSession):
    from karakara.model import commit
    return commit


@pytest.fixture()
def settings(request, app):
    return app.app.registry.settings
