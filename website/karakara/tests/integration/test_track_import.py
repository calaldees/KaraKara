import json

def assert_base_track_ids(app, ids={'t1', 't2', 't3', 'xxx'}):
    response = app.get('/track_import?format=json')
    assert set(response.json['data']['track_ids']) == ids


def app_request_json(app, url, data={}, method='post'):
    getattr(app, method)(url, json.dumps(data), headers={'content-type': 'application-json'})


def test_track_import_without_data(app):
    app.post(
        '/track_import?format=json',
        {'form': 'should reject form data as we require json'},
        status=400,
        expect_errors=True
    )


def test_track_import(app, tracks):
    assert_base_track_ids(app)

    app_request_json(app, '/track_import?format=json', {
        'tracks': [
            {'id': 'test1'},
            {'id': 'test2'},
        ],
    })

    assert_base_track_ids(app)


def test_track_import_put_delete(app, tracks):
    assert_base_track_ids(app)

    response = app.get('/track_import?format=json', )

    assert_base_track_ids(app)