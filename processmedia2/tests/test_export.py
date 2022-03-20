import pytest
import tempfile
import json
import operator

from export_track_data import export_track_data


def test_export_full(ProcessMediaTestManager, TEST1_VIDEO_FILES, TEST2_AUDIO_FILES):
    """
    Test the entire Scan, Encode, Import cycle with a video and audio item
    """
    track_file = tempfile.NamedTemporaryFile().name   #'/static/tracks.json'
    with ProcessMediaTestManager(TEST1_VIDEO_FILES | TEST2_AUDIO_FILES) as manager:
        manager.scan_media()
        manager.encode_media(mock=True)
        stats = export_track_data(path_static_track_list=track_file, **manager.commandline_kwargs)

        assert stats == {
            'meta_exported': {'test2', 'test1'},
            'meta_unprocessed': set(),
            'missing_processed_aborted': set(),
            'missing_processed_deleted': set(),
        }

        # Load the exported track json data
        with open(track_file, 'rt') as filehandle:
            data = json.load(filehandle)

        # Load all metadata of processed items
        mm = manager.meta_manager
        mm.load_all()

        # Check that expected source files are in the exported data
        EXPECTED_TRACKS = frozenset(('track1', 'track2'))
        for track in data.values():
            name = track['source_filename']
            name in EXPECTED_TRACKS
            assert frozenset(track.keys()) == {"source_filename", "duration", "attachments", "srt", "tags"}
            assert frozenset(map(operator.itemgetter('use'), track['attachments'])) == {'image', 'video', 'preview','srt', 'tags'}
            # Check srt content
            with open(mm.get(name).processed_files['srt'].absolute, 'rt') as filehandle:
                assert  track['srt'] in filehandle.read()
            # Check tag content
            with open(mm.get(name).processed_files['tags'].absolute, 'rt') as filehandle:
                assert track['tags'] in filehandle.read()
