import pytest

from karakara.model.init_data import init_data
from model.model_tracks import Track  #, Tag, Attachment, _attachment_types

from import_media import import_media
from ._base import ScanManager, TEST1_VIDEO_FILES, TEST2_AUDIO_FILES

import logging
log = logging.getLogger(__name__)

INI = '../website/test.ini'


@pytest.fixture(scope="session")
def DBSession(request, ini_file=INI):
    """
    Aquire standalone DBSession for karakara webapp
    """
    from pyramid.paster import get_appsettings
    from karakara.model import DBSession, init_DBSession
    init_DBSession(get_appsettings(ini_file))
    #init_data()
    return DBSession


def test_import_simple(DBSession):
    with ScanManager(TEST1_VIDEO_FILES + TEST2_AUDIO_FILES) as scan:
        scan.scan_media()
        scan.encode_media()

        import_media(path_meta=scan.path_meta, path_processed=scan.path_processed)
