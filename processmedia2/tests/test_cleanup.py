import os.path
from itertools import chain

from ._base import ProcessMediaTestManager


def test_cleanup_media():

    def make_hash_dict(name):
        return {
            "media": "{}_media".format(name),
            "data": "{}_data".format(name),
        }

    def processed_files_for_source_hashs(hash_dict):
        return {
            processed_file.relative
            for processed_file in manager.processed_files_manager.get_processed_files(hash_dict).values()
        }

    with ProcessMediaTestManager() as manager:
        manager.meta = {
            "test11.json": {
                "processed": {
                    "hashs": make_hash_dict('test11_hash'),
                },
            },
            "test12.json": {
                "processed": {
                    "hashs": make_hash_dict('test12_hash'),
                }
            },
        }
        processed_files_for_test11 = processed_files_for_source_hashs(make_hash_dict('test11_hash'))
        processed_files_for_test12 = processed_files_for_source_hashs(make_hash_dict('test12_hash'))
        manager.mock_processed_files(chain(processed_files_for_test11, processed_files_for_test12))
        manager.meta = {
            "test11.json": {
                "processed": {
                    "hashs": make_hash_dict('test11_hash'),
                },
            },
        }

        manager.cleanup_media()

        assert all(
            os.path.exists(os.path.join(manager.path_processed, relative_filename))
            for relative_filename in processed_files_for_test11
        ), 'All files from test11 should still be present {}'.format(processed_files_for_test11)

        assert not any(
            os.path.exists(os.path.join(manager.path_processed, relative_filename))
            for relative_filename in processed_files_for_test12
        ), 'All files from test12 should have been deleted {}'.format(processed_files_for_test12)
