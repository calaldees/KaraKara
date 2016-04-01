import pytest
from collections import defaultdict

from libs.misc import flatten, freeze

from import_media import import_media

from karakara.model.model_tracks import Track, Tag, Attachment, _attachment_types
from karakara.model.actions import get_track_dict_full, get_tag

from karakara.tests.data.tracks import AttachmentDescription, create_test_track



from ._base import ProcessMediaTestManager, TEST1_VIDEO_FILES, TEST2_AUDIO_FILES

import logging
log = logging.getLogger(__name__)

INI = '../website/test.ini'


EXPECTED_ATTACHMENT_COUNT = freeze(dict(image=4, preview=1, video=1, srt=1))


def get_source_hashs(meta):
    return (data['processed']['source_hash'] for data in meta.values())


@pytest.fixture(scope="session")
def DBSession_base(request, ini_file=INI):
    """
    Aquire standalone DBSession for karakara webapp
    """
    from pyramid.paster import get_appsettings
    from import_media import init_DBSession, DBSession
    init_DBSession(get_appsettings(ini_file))
    return DBSession


@pytest.fixture(scope="function")
def DBSession(request, DBSession_base):
    from karakara.model.init_data import init_data
    init_data()
    return DBSession_base


@pytest.fixture(scope="session")
def commit(request, DBSession_base):
    """
    Save data attached to DBSession
    """
    from import_media import commit
    return commit




def _est_import_full(DBSession):
    with ProcessMediaTestManager(TEST1_VIDEO_FILES | TEST2_AUDIO_FILES) as manager:
        manager.scan_media()
        manager.encode_media()
        stats = import_media(path_meta=manager.path_meta, path_processed=manager.path_processed)

        assert freeze(stats) == freeze(dict(total=2, imported=2, unprocessed=0, missing=0, deleted=0, before=0, processed=2))

        track1 = get_track_dict_full(manager.get_source_hash('test1'))
        import pdb ; pdb.set_trace()
        track2 = get_track_dict_full(manager.get_source_hash('test2'))


def test_basic_import(DBSession):
    with ProcessMediaTestManager() as manager:

        # Create mock scan data (as if an encode had just been performed)
        manager.meta = {
            "test3.json": {
                "processed": {
                    "source_hash": "test3_hash",
                },
            },
            "test4.json": {
                "processed": {
                    "source_hash": "test4_hash",
                }
            },
        }

        # Create empty files for all expected processed files
        manager.mock_processed_files(
            processed_file.absolute for processed_file in flatten(
                manager.get_all_processed_files_associated_with_source_hash(source_hash).values()
                for source_hash in get_source_hashs(manager.meta)
            )
        )

        stats = import_media(path_meta=manager.path_meta, path_processed=manager.path_processed)

        assert freeze(stats) == freeze(dict(total=2, imported=2, unprocessed=0, missing=0, deleted=0, before=0, processed=2))
        assert DBSession.query(Track).count() == 2

        def count_attachments(track):
            attachments = defaultdict(int)
            for attachment in track['attachments']:
                attachments[attachment['type']] += 1
            return dict(attachments)

        track3 = get_track_dict_full('test3_hash')
        assert freeze(count_attachments(track3)) == EXPECTED_ATTACHMENT_COUNT

        track4 = get_track_dict_full('test4_hash')
        assert freeze(count_attachments(track4)) == EXPECTED_ATTACHMENT_COUNT


def test_import_side_effects():
    """
    If a source fileset is incomplete and exisits in db - it is removed from the db - missing
    If a source fileset is missing and exists in db - it is removed - missing
    If source fileset is incomplete and not exisit in db - it is never added - unprocessed?
    If a file existed before the import began is has all source files it is kept - before
    """
    create_test_track('test5', )
    with ProcessMediaTestManager() as manager:
        manager.meta = {
            "test5.json": {
                "processed": {
                    "source_hash": "test5_hash",
                    "duration": 15.0,
                }
            },
            "test6.json": {
                "processed": {
                    "source_hash": "test6_hash",
                    "duration": 15.0,
                }
            },
            "test7.json": {
                "processed": {
                    "source_hash": "test7_hash",
                    "duration": 15.0,
                }
            },
            "test8.json": {
                "processed": {
                    "source_hash": "test8_hash",
                    "duration": 15.0,
                }
            }
        }
