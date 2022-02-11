import pytest

import re
import json
import tempfile
import pathlib

from unittest.mock import patch



def _track_import(app, url='/track_import?format=json', json_data={}, method='get'):
    return getattr(app, method)(url, json.dumps(json_data), headers={'content-type': 'application-json'})


def _assert_base_tracks(app, ids={'t1', 't2', 't3', 'xxx'}):
    response = _track_import(app)
    assert response.json['data']['tracks'] == {'t1': 'track1source', 't2': 'track2source', 't3': 'track3source', 'xxx': 'wildcardsource'}


def test_track_import_without_data(app):
    app.post(
        '/track_import?format=json',
        {'form': 'should reject form data as we require json'},
        status=400,
        expect_errors=True
    )


def test_track_import_delete(app, queue, tracks, registry_settings):
    _assert_base_tracks(app)

    track_import1_source = {
        'id': 'import1',
        'source_filename': 'import1_filename1',
        'duration': 120.0,
        'srt': re.sub(r'^\s*', '', '''
            1
            00:00:13,500 --> 00:00:22,343
            test, it's, ここにいくつかのテキストです。
        '''),
        'attachments': [
            {'type': 'image', 'location': '/test/import1.jpg'},
        ],
        'tags': ['category:test', 'title:Import Test'],
    }

    track_version = registry_settings['karakara.tracks.version']
    _track_import(app, method='post', json_data=[track_import1_source])
    assert 'import1' in _track_import(app, method='get').json['data']['tracks']
    assert track_version != registry_settings['karakara.tracks.version']

    track_import1 = app.get(f'/queue/{queue}/track/import1?format=json').json['data']['track']
    for key in ('id', 'duration', 'srt', 'source_filename'):
        assert track_import1_source[key] == track_import1[key]
    assert track_import1['title'] == 'Import Test'
    assert '/test/import1.jpg' in (attachment['location'] for attachment in track_import1['attachments'])
    assert {'category', 'title'} < track_import1['tags'].keys()

    track_version = registry_settings['karakara.tracks.version']
    _track_import(app, method='delete', json_data=['import1'])
    _assert_base_tracks(app)
    assert track_version != registry_settings['karakara.tracks.version']


def test_track_import_update(app, queue, tracks, registry_settings):
    with tempfile.TemporaryDirectory() as tempdir:
        with patch.dict(registry_settings, {'static.path.output': tempdir}):  # it is ok to patch the raw setting dict as this is never exposed by the settings api so we don't need temporary_settings
            _track_import(app, method='patch')  # trigger generation of `track_list.json`
        # Files created a json and in the same format as `/queue/QUEUE/track_list.json`
        data = json.load(
            pathlib.Path(tempdir).joinpath('queue', queue, 'track_list.json').open()
        )
        assert data['data']['list'], 'static json track list should have tracks in'
        assert 'test track 3 キ' in {track['title'] for track in data['data']['list']}  # double check unicode from static file process
