import pytest

import logging
log = logging.getLogger(__name__)


#@pytest.fixture(autouse=True)
class TestKaraKara():
    @classmethod
    def setup_class(cls):
        """
        """
        log.info("setup")
    
    @classmethod
    def teardown_class(cls):
        """
        """
        log.info("teardown")
    
    #def test_example(self, example):
    #    print('example {0}'.format(example))
    #    assert False

    def test_db(self, tracks):
        print('base_data')
        
