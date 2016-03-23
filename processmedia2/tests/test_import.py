import pytest
from karakara.tests import conftest

from model.model_tracks import Track, Tag, Attachment, _attachment_types

import logging
log = logging.getLogger(__name__)

INI = '../website/test.ini'



@pytest.fixture(scope="session")
def app_ini(request, ini_file=INI):
    """
    Settings object derived from .ini file
    We are only interested in the database settings
    """
    from pyramid.paster import get_appsettings
    return get_appsettings(ini_file)


@pytest.fixture(scope="session")
def DBSession(request, app_ini):
    """
    Aquire standalone DBSession for karakara webapp
    """
    from karakara.model import DBSession, init_DBSession
    init_DBSession(app_ini)
    return DBSession


def test_example(DBSession):
    assert False
