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


EXPECTED_ATTACHMENT_COUNT = freeze(dict(image=4, preview=1, video=1, srt=1, tags=1))


def get_source_hashs_from_scan_meta(meta):
    return (data['processed']['source_hash'] for data in meta.values())


def get_attachment_descriptions(processed_files):
    return (
        AttachmentDescription(processed_file.relative, attachment_type)
        for attachment_type, processed_file_list in processed_files.items()
        for processed_file in processed_file_list
    )


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


def _est_basic_import(DBSession):
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
            processed_file.relative for processed_file in flatten(
                manager.get_all_processed_files_associated_with_source_hash(source_hash).values()
                for source_hash in get_source_hashs_from_scan_meta(manager.meta)
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


def test_import_side_effects(DBSession, commit):
    """
    If a source fileset is incomplete and exisits in db - it is removed from the db - missing
    If a source fileset is missing and exists in db - it is removed - missing
    If source fileset is incomplete and not exisit in db - it is never added - unprocessed?
    If a file existed before the import began is has all source files it is kept - before
    """
    with ProcessMediaTestManager() as manager:

        def get_attachments(source_hash):
            return get_attachment_descriptions(
                manager.get_all_processed_files_associated_with_source_hash(source_hash)
            )

        # Test5 is an existing complete track already db - all processed files present
        track5_attachments = get_attachments('test5_hash')
        create_test_track(
            'test5_hash',
            attachments=track5_attachments,
            tags=(),
            lyrics='',
            source_filename='',
        )
        manager.mock_processed_files(attachment_description.location for attachment_description in track5_attachments)
        commit()

        # Test7 exisits in db - will be missing one file from the processed folder
        track7_attachments = get_attachments('test7_hash')
        create_test_track(
            'test7_hash',
            attachments=track7_attachments,
            tags=(),
            lyrics='',
            source_filename='',
        )
        manager.mock_processed_files(a.location for a in track7_attachments if a.type != 'preview')
        commit()

        # Test8 exisiting complete track in db - no meta data matches this entry
        track8_attachments = get_attachments('test8_hash')
        create_test_track(
            'test8_hash',
            attachments=track8_attachments,
            tags=(),
            lyrics='',
            source_filename='',
        )
        manager.mock_processed_files(a.location for a in track8_attachments if a.type != 'preview')
        commit()

        manager.meta = {
            # Test5 should be fine
            "test5.json": {
                "processed": {
                    "source_hash": "test5_hash",
                    "duration": 15.0,
                }
            },
            # Test6 has not be encoded/processed yet and has no source hash
            "test6.json": {
                "processed": {
                    #"source_hash": "test6_hash",
                    "duration": 15.0,
                }
            },
            # Test7 is incomplete on disk and missing processed file even though the meta exists 
            "test7.json": {
                "processed": {
                    "source_hash": "test7_hash",
                    "duration": 15.0,
                }
            },
            # Test 8 does not exist in meta

            # Test9 is a completly new track
            "test9.json": {
                "processed": {
                    "source_hash": "test9_hash",
                    "duration": 15.0,
                }
            },
        }

        stats = import_media(path_meta=manager.path_meta, path_processed=manager.path_processed)

        assert freeze(stats) == freeze(dict(
            total=2,  # test5, test9
            imported=1,  # test9
            unprocessed=1,  # test6
            missing=1,  # test7
            deleted=1,  # test8
            existing=3,  # test5, test7, test8
            processed=3,  # test5, test9, test7
            existing_=1,  # test5
        ))
        assert DBSession.query(Track).count() == 2
        assert DBSession.query(Track).get('test5')
        assert DBSession.query(Track).get('test9')
