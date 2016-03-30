import pytest
from itertools import chain

from karakara.model.init_data import init_data
from karakara.model.model_tracks import Track  #, Tag, Attachment, _attachment_types

from import_media import import_media

from ._base import ProcessMediaTestManager, TEST1_VIDEO_FILES, TEST2_AUDIO_FILES

import logging
log = logging.getLogger(__name__)

INI = '../website/test.ini'

MOCK_IMPORT_JSON = {
    "test2.json": {
        "actions": [],
        "processed": {
            "width": 640,
            "source_hash": "88bd2fc97bc72851c72b7ca87b9ba815ec8f75519152a4f7dda5d929756a980b",
            "duration": 15.0,
            "height": 400
        },
        "scan": {
            "test2.png": {
                "hash": "96406d58bcc88992945fe71ec78d6b31936129406a76d2eb4e18441b27bf46a1",
                "relative": "test2.png",
                "mtime": 1458845841
            },
            "test2.ssa": {
                "hash": "d7ae728051b2fdafc3dc479bb9dedf7049a6393d473f114c663c1c93a9f60997",
                "relative": "test2.ssa",
                "mtime": 1458845992
            },
            "test2.txt": {
                "hash": "23a39acb1f53878f0b89df3610f37514aeb27aca589e0d471daeaa6bc5992957",
                "relative": "test2.txt",
                "mtime": 1458805266
            },
            "test2.ogg": {
                "hash": "cc2da32e124beb450c53a98dbd25d5670ce5ea346eab6d4159b37c325645240a",
                "relative": "test2.ogg",
                "mtime": 1458844256
            }
        }
    },
    "test1.json": {
        "actions": [],
        "processed": {
            "width": 640,
            "audio": {
                "bitrate": "2",
                "sample_rate": "44100",
                "format": "aac"
            },
            "source_hash": "68676f44efc5d0ebe4a1abece95685f25d6373decf9699cac0e19f2d17019eed",
            "duration": 30.02,
            "height": 480
        },
        "scan": {
            "test1.txt": {
                "hash": "06017988c3548e0613f0ac5d5298af2beded28987009e635dbb55a9260e000cd",
                "relative": "test1.txt",
                "mtime": 1458805286
            },
            "test1.mp4": {
                "hash": "9d2aa602b76f0646b7807e24673d51a37c295b242726b20d37af7f407e0e75c8",
                "relative": "test1.mp4",
                "mtime": 1458683515
            },
            "test1.srt": {
                "hash": "9b15dd2988f1856f8af387d927b70d39515fde91af6aa5fada4f64056b8b78c1",
                "relative": "test1.srt",
                "mtime": 1458287540
            }
        }
    }
}


def get_source_hashs(meta):
    return (data['processed']['source_hash'] for data in meta.values())


@pytest.fixture(scope="session")
def DBSession_base(request, ini_file=INI):
    """
    Aquire standalone DBSession for karakara webapp
    """
    from pyramid.paster import get_appsettings
    from karakara.model import DBSession, init_DBSession
    init_DBSession(get_appsettings(ini_file))
    return DBSession


@pytest.fixture(scope="function")
def DBSession(request, DBSession_base):
    init_data()
    return DBSession_base


def test_import_full(DBSession):
    with ProcessMediaTestManager(TEST1_VIDEO_FILES | TEST2_AUDIO_FILES) as manager:
        manager.scan_media()
        #manager.encode_media()
        #import pdb ; pdb.set_trace()
        #import_media(path_meta=manager.path_meta, path_processed=manager.path_processed)


def test_basic_import(DBSession):
    with ProcessMediaTestManager() as manager:

        # Create mock scan data (as if an encode had just been performed)
        manager.meta = MOCK_IMPORT_JSON

        # Create empty files for all expected processed files
        manager.mock_processed_files(
            processed_file.absolute for processed_file in chain(*(chain(*(
                manager.get_all_processed_files_associated_with_source_hash(source_hash).values()
                for source_hash in get_source_hashs(manager.meta)
            ))))
        )

        # Attempt import
        import_media(DBSession, path_meta=manager.path_meta, path_processed=manager.path_processed)

        # Assert tracks are in DB
        assert DBSession.query(Track).count() == 2
