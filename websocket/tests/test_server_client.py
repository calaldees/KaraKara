import pytest
import logging
import socket
import time

from ..server import Server


log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(process)d %(name)s: %(message)s')


# Fixtures ---------------------------------------------------------------------

@pytest.fixture(scope='session')
def server():
    server = Server()
    yield server


# Tests ------------------------------------------------------------------------

def test_stub(server):
    assert True
