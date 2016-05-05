import pytest

from ._base import ProcessMediaTestManager, TEST1_VIDEO_FILES, TEST2_AUDIO_FILES

from metaviewer import MetaViewer


def test_metaviewer():
    with ProcessMediaTestManager(TEST1_VIDEO_FILES | TEST2_AUDIO_FILES) as manager:
        metaviewer = MetaViewer(path_meta=manager.path_meta, path_processed=manager.path_processed, path_source=manager.path_source)

        # No meta files have been created yet
        file_details = metaviewer.get_meta_details('test1')
        assert len(file_details.keys()) == 0

        # Create meta files
        manager.scan_media()

        file_details = metaviewer.get_meta_details('test1')
        assert len(file_details.keys()) == 1
        test1_details = file_details['test1']
        for f in test1_details:
            if f.type == 'source':
                assert f.exists()
            if f.type == 'processed':
                assert not f.exists()

        file_details = metaviewer.get_meta_details('test2')
        assert len(file_details.keys()) == 1
        assert 'test2' in file_details

        # Todo ... assert the processed files exists? Maybe just creating a few in the correct place?
