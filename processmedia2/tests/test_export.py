import pytest
import tempfile

from export_media import export_media


def test_export_full(ProcessMediaTestManager, TEST1_VIDEO_FILES, TEST2_AUDIO_FILES):
    """
    Test the entire Scan, Encode, Import cycle with a video and audio item
    """
    with ProcessMediaTestManager(TEST1_VIDEO_FILES | TEST2_AUDIO_FILES) as manager:
        manager.scan_media()
        manager.encode_media(mock=True)
        stats = export_media(path_static_track_list='/static/tracks.json', **manager.commandline_kwargs)

        assert stats == {
            'meta_exported': {'test2', 'test1'},
            'meta_unprocessed': set(),
            'missing_processed_aborted': set(),
            'missing_processed_deleted': set(),
        }
