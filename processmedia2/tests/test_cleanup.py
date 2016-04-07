import os.path
from itertools import chain

from libs.misc import flatten, freeze

from ._base import ProcessMediaTestManager

from cleanup_media import cleanup_media


def test_cleanup_media():

    def processed_files_for_source_hash(source_hash):
        return (processed_file.relative for processed_file in flatten(
            manager.get_all_processed_files_associated_with_source_hash(source_hash).values()
        ))


    with ProcessMediaTestManager() as manager:
        manager.meta = {
            "test11.json": {
                "processed": {
                    "source_hash": "test11_hash",
                },
            },
            "test12.json": {
                "processed": {
                    "source_hash": "test12_hash",
                }
            },
        }
        processed_files_for_test11 = processed_files_for_source_hash('test11_hash')
        processed_files_for_test12 = processed_files_for_source_hash('test12_hash')
        manager.mock_processed_files(chain(processed_files_for_test11, processed_files_for_test12))
        manager.meta = {
            "test11.json": {
                "processed": {
                    "source_hash": "test11_hash",
                },
            },
        }

        cleanup_media(path_meta=manager.path_meta, path_processed=manager.path_processed)

        assert all(os.path.exists(os.path.join(manager.path_processed, relative_filename)) for relative_filename in processed_files_for_test11)
        assert not any(os.path.exists(os.path.join(manager.path_processed, relative_filename)) for relative_filename in processed_files_for_test12)
