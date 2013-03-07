import pytest

import logging
log = logging.getLogger(__name__)

import pyramid.request



#@pytest.fixture(autouse=True)
class TestKaraKara():
    @classmethod
    def setup_class(cls):
        """
        """
        log.info("setup")
        log.debug("debug test message")
        log.info("info test message")
        log.warn("warning test message")
        log.error("error test message")
    
    @classmethod
    def teardown_class(cls):
        """
        """
        log.info("teardown")
    
    #def test_example(self, example):
    #    print('example {0}'.format(example))
    #    assert False

    def test_db(self, tracks):
        pass
        #print('base_data')
        #assert False
        
