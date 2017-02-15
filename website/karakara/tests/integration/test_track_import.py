import json


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


def test_track_import_delete(app, tracks):
    _assert_base_tracks(app)

    _track_import(
        app,
        method='post',
        json_data=[{
            'id': 'import1',
            'source_filename': 'import1_filename1',
            'duration': 120,
            'lyrics': 'la la la\nle le le',
            'attachments': [
                {'type': 'image', 'location': '/test/import1.jpg'},
            ],
            'tags': ['category:test', 'title:import1'],
        }],
    )

    assert 'import1' in _track_import(app, method='get').json['data']['tracks']
    #TODO: Assert track data is in db. Perform json get on track?

    _track_import(
        app,
        method='delete',
        json_data=['import1'],
    )

    _assert_base_tracks(app)
