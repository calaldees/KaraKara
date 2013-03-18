import pytest

import logging
log = logging.getLogger(__name__)

INI = 'test.ini'

from karakara.tests.data.tracks import *

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
    from karakara.model import DBSession, init_db
    init_db()
    return DBSession

@pytest.fixture(scope="session")
def commit(request, DBSession):
    from karakara.model import commit
    return commit