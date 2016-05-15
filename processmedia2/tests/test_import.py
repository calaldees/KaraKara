import pytest
from collections import defaultdict

from libs.misc import flatten, freeze

from import_media import import_media

from karakara.model.model_tracks import Track, Tag, Attachment, _attachment_types
from karakara.model.actions import get_track_dict_full, get_tag

from karakara.tests.data.tracks import AttachmentDescription, create_test_track



from ._base import ProcessMediaTestManager, TEST1_VIDEO_FILES, TEST2_AUDIO_FILES
from processmedia_libs.meta_manager import MetaFile

import logging
log = logging.getLogger(__name__)

INI = '../website/test.ini'


EXPECTED_ATTACHMENT_COUNT = freeze(dict(image=4, preview=1, video=1, srt=1, tags=1))


def get_attachment_descriptions(processed_files):
    return tuple(
        AttachmentDescription(processed_file.relative, processed_file.attachment_type)
        for processed_file in processed_files.values()
    )

def gen_fake_hash_dict(source_hash):
    return {
        MetaFile.SOURCE_HASH_FULL_KEY: source_hash,
        "media": "{}_media".format(source_hash),
        "data": "{}_data".format(source_hash),
    }


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




def test_import_full(DBSession):
    """
    Test the entire Scan, Encode, Import cycle with a video and audio item
    """
    with ProcessMediaTestManager(TEST1_VIDEO_FILES | TEST2_AUDIO_FILES) as manager:
        manager.scan_media()
        manager.encode_media()
        stats = import_media(**manager.commandline_kwargs)

        assert freeze(stats) == freeze(dict(
            db_end={'test1', 'test2'},
            meta_imported={'test1', 'test2'},
            meta_unprocessed={},
            missing_processed_deleted={},
            missing_processed_aborted={},
            db_removed=[],
            db_start={},
            meta_set={'test1', 'test2'},
            meta_hash_matched_db_hash={},
        ))

        track1 = get_track_dict_full(manager.get('test1').source_hash)
        assert track1

        track2 = get_track_dict_full(manager.get('test2').source_hash)
        assert track2

        # TODO: assertions on db tracks


def test_basic_import(DBSession):
    """
    Fake import cycle into db with mocked processed files for simple case
    """
    with ProcessMediaTestManager() as manager:

        # Create mock scan data (as if an encode had just been performed)
        manager.meta = {
            "test3.json": {
                "processed": {
                    MetaFile.SOURCE_HASHS_KEY: gen_fake_hash_dict("test3_hash"),
                },
            },
            "test4.json": {
                "processed": {
                    MetaFile.SOURCE_HASHS_KEY: gen_fake_hash_dict("test4_hash"),
                },
            },
        }

        # Create empty files for all expected processed files
        manager.mock_processed_files(
            processed_file.relative
            for m in manager.meta_manager.meta_items
            for processed_file in m.processed_files.values()
        )

        stats = import_media(**manager.commandline_kwargs)

        assert freeze(stats) == freeze(dict(
            db_end={'test3', 'test4'},
            meta_imported={'test3', 'test4'},
            meta_unprocessed={},
            missing_processed_deleted={},
            missing_processed_aborted={},
            db_removed=[],
            db_start={},
            meta_set={'test3', 'test4'},
            meta_hash_matched_db_hash={},
        ))
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

def test_import_rejected_triggerer_reencode():
    # TODO: Implement
    pass

def test_import_side_effects(DBSession, commit):
    """
    Test mocked complex import cycle.
    Exercising various existing tracks and meta/processed tracks
    This should test all known common flows
    """
    with ProcessMediaTestManager() as manager:

        def get_attachments(name):
            return get_attachment_descriptions(
                manager.meta_manager.processed_files_manager.get_processed_files(gen_fake_hash_dict(name))
            )

        # Test5 is an existing complete track already db - all processed files present
        track5_attachments = get_attachments('test5_hash')
        create_test_track(
            'test5_hash',
            attachments=track5_attachments,
            tags=(),
            lyrics='',
            source_filename='test5',
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
            source_filename='test7',
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
            source_filename='test8',
        )
        manager.mock_processed_files(a.location for a in track8_attachments)
        commit()

        manager.meta = {
            # Test5 should exist in db and match this meta. No op required
            "test5.json": {
                "processed": {
                    MetaFile.SOURCE_HASHS_KEY: gen_fake_hash_dict("test5_hash"),
                    "duration": 15.0,
                }
            },
            # Test6 has not be encoded/processed yet and has no source hash
            "test6.json": {
                "processed": {
                    #MetaFile.SOURCE_HASHS_KEY: gen_fake_hash_dict("test6_hash"),
                    "duration": 15.0,
                }
            },
            # Test7 is incomplete on disk and missing processed file even though the meta exists 
            "test7.json": {
                "processed": {
                    MetaFile.SOURCE_HASHS_KEY: gen_fake_hash_dict("test7_hash"),
                    "duration": 15.0,
                }
            },
            # Test 8 does not exist in meta

            # Test9 is a completly new track and will be imported cleanly - Creation of mock processed files below
            "test9.json": {
                "processed": {
                    MetaFile.SOURCE_HASHS_KEY: gen_fake_hash_dict("test9_hash"),
                    "duration": 15.0,
                }
            },
            # test10 is processed but has incomplete processed files
            "test10.json": {
                "processed": {
                    MetaFile.SOURCE_HASHS_KEY: gen_fake_hash_dict("test10_hash"),
                    "duration": 15.0,
                }
            },
        }
        manager.mock_processed_files(
            processed_file.relative
            for processed_file in manager.meta_manager.get('test9').processed_files.values()
        )
        manager.mock_processed_files(
            processed_file.relative
            for processed_file in tuple(
                manager.meta_manager.get('test10').processed_files.values()
            )[:len(_attachment_types.enums)-2]  # Remove a couple of required files
        )

        stats = import_media(**manager.commandline_kwargs)

        assert freeze(stats) == freeze(dict(
            db_end={'test5', 'test9'},
            meta_imported={'test9'},
            meta_unprocessed={'test6'},
            missing_processed_deleted={'test7'},
            missing_processed_aborted={'test10'},
            db_removed=['test8'],
            db_start={'test5', 'test7', 'test8'},
            meta_set={'test5', 'test7', 'test9', 'test10'},
            meta_hash_matched_db_hash={'test5'},
        ))
        assert DBSession.query(Track).count() == 2
        assert DBSession.query(Track).get('test5_hash')
        assert DBSession.query(Track).get('test9_hash')
