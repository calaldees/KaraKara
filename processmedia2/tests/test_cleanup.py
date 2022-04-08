import os.path
from itertools import chain


def test_cleanup_media(ProcessMediaTestManager):

    def processed_files_for_source_hashs(hash_dict):
        return {
            processed_file.file
            for processed_file in manager.processed_files_manager.get_processed_files(hash_dict).values()
        }

    with ProcessMediaTestManager() as manager:
        manager.meta = {
            "test11.json": {
                "scan": {
                    "not_real1.mp4": {"hash": "test11_hash", "relative": "not_real1.mp4", "mtime": 0},
                },
            },
            "test12.json": {
                "scan": {
                    "not_real2.mp4": {"hash": "test12_hash", "relative": "not_real2.mp4", "mtime": 0},
                },
            },
        }
        processed_files_for_test11 = processed_files_for_source_hashs(('test11_hash',))
        processed_files_for_test12 = processed_files_for_source_hashs(('test12_hash',))
        manager.mock_processed_files(chain(processed_files_for_test11, processed_files_for_test12))
        manager.meta = {
            "test11.json": {
                "scan": {
                    "not_real1.mp4": {"hash": "test11_hash", "relative": "not_real1.mp4", "mtime": 0},
                },
            },
            # remove "test12.json" metadata
        }

        manager.cleanup_media()

        # os.path.exists(os.path.join(manager.path_processed, relative_filename))
        assert all(f.is_file() for f in processed_files_for_test11), f'All files from test11 should still be present {processed_files_for_test11}'

        assert not any(f.is_file() for f in processed_files_for_test12), f'All files from test12 should have been deleted {processed_files_for_test12}'
