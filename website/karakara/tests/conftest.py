import pytest

import logging
log = logging.getLogger(__name__)

INI = 'test.ini'

@pytest.fixture(scope="session")
def app(request):
    from webtest import TestApp
    from pyramid.paster import get_appsettings
    from karakara import main as karakara_main
    
    #print('setup WebApp')
    application = karakara_main({}, **get_appsettings(INI))
    app = TestApp(application)
    
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