import pytest
import tempfile
import json
import operator
import numbers
from itertools import chain

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
        assert frozenset(('test1', 'test2')) == frozenset(track['source_filename'] for track in data.values())

        for track_id, track in data.items():
            assert track_id == track['id']
            assert frozenset(track.keys()) == {"id", "source_hash", "source_filename", "duration", "attachments", "lyrics", "tags"}

            assert track['duration']
            assert isinstance(track['duration'], numbers.Number)

            track['attachments'].keys() == {'video', 'preview', 'image', 'subtitle'}

            mimes = frozenset(map(operator.itemgetter('mime'), chain.from_iterable(track['attachments'].values())))
            #{'image/avif', 'image/webp', 'text/vtt'}  # TODO: assert something about mimes

            assert track['lyrics']
            # Check tag content
            assert frozenset(track['tags'].keys()) >= frozenset(('title', 'category', 'artist', 'from'))
