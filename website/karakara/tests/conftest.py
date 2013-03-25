import pytest

import logging
log = logging.getLogger(__name__)

INI = 'test.ini'

from karakara.tests.data.tracks import *

# Markers ----------------------------------------------------------------------

#def pytest_addoption(parser):
#    parser.addoption("--runslow", action="store_true", help="run slow tests")
def pytest_runtest_setup(item):
    if 'unimplemented' in item.keywords: #and not item.config.getoption("--runslow"):
        pytest.skip('unimplemented functionality') #"need --runslow option to run"
    if 'unfinished' in item.keywords:
        pytest.skip('unfinished functionality') #"need --runslow option to run"

unimplemented = pytest.mark.unimplemented # Server dose not support the functionlity this test is asserting yet
unfinished    = pytest.mark.unfinished    # The test is unfinished and currently is know to fail
xfail         = pytest.mark.xfail
# Fixtures ---------------------------------------------------------------------

@pytest.fixture(scope="session")
def settings(request):
    from pyramid.paster import get_appsettings
    return get_appsettings(INI)

@pytest.fixture(scope="session")
def app(request, settings):
    from webtest import TestApp
    from karakara import main as karakara_main
    
    #print('setup WebApp')
    app = TestApp(karakara_main({}, **settings))
    
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
    from karakara.model.init_data import init_data
    init_data()
    return DBSession

@pytest.fixture(scope="session")
def commit(request, DBSession):
    from karakara.model import commit
    return commit
