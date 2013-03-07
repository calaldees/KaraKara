# http://sontek.net/blog/detail/writing-tests-for-pyramid-and-sqlalchemy

import unittest
import pyramid.testing
from paste.deploy.loadwsgi import appconfig

#from webtest import TestApp
#from mock import Mock

#from sqlalchemy import engine_from_config
#import sqlalchemy.orm
#from app.db import Session
#from app.db import Entity  # base declarative object
#from app import main
#import os
#here = os.path.dirname(__file__)
#settings = appconfig('config:' + os.path.join(here, '../../', 'test.ini'))

from pyramid.paster import get_appsettings
settings = get_appsettings('test.ini')

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = engine_from_config(settings, prefix='sqlalchemy.')
        cls.Session = sqlalchemy.orm.sessionmaker()

    def setUp(self):
        connection = self.engine.connect()
        # begin a non-ORM transaction
        self.trans = connection.begin()
        # bind an individual Session to the connection
        Session.configure(bind=connection)
        self.session = self.Session(bind=connection)
        Entity.session = self.session

    def tearDown(self):
        # rollback - everything that happened with the
        # Session above (including calls to commit())
        # is rolled back.
        testing.tearDown()
        self.trans.rollback()
        self.session.close()


class UnitTestBase(BaseTestCase):
    def setUp(self):
        self.config = pyramid.testing.setUp(request=pyramid.testing.DummyRequest())
        super(UnitTestBase, self).setUp()

    def get_csrf_request(self, post=None):
        csrf = 'abc'

        if not 'csrf_token' in post.keys():
            post.update({
                'csrf_token': csrf
            })

        request = pyramid.testing.DummyRequest(post)

        request.session = Mock()
        csrf_token = Mock()
        csrf_token.return_value = csrf

        request.session.get_csrf_token = csrf_token

        return request


#class IntegrationTestBase(BaseTestCase):
class IntegrationTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = main({}, **settings)
        super(IntegrationTestBase, cls).setUpClass()

    def setUp(self):
        self.app = TestApp(self.app)
        self.config = testing.setUp()
        super(IntegrationTestBase, self).setUp()