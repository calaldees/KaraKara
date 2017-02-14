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


def test_track_import(app, tracks):
    _assert_base_tracks(app)

    _track_import(
        app,
        method='post',
        json_data={
            'tracks': [
                {'id': 'test1'},
                {'id': 'test2'},
            ],
        },
    )

    _assert_base_tracks(app)


def test_track_import_put_delete(app, tracks):
    pass
