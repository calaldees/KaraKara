## -*- coding: utf-8 -*-

import pytest

test_formats = ['html'] #, 'json', 'xml'

def pytest_generate_tests (metafunc):
    if 'format' in metafunc.fixturenames:
        metafunc.parametrize('format', test_formats)
@pytest.mark.parametrize(('track_id', 'expected_response', 'text_list',), [
    ('t1', 200, ['Test Track 1'   , 'series X', 'anime', 'ここ', 'test/image1.jpg'  ]),
    ('t2', 200, ['Test Track 2'   , 'series X', 'anime', 'äöü', 'test/preview2.flv']),
    ('t3', 200, ['Test Track 3 キ', 'series Y', 'anime',        'test/preview3.mp4']),
    #('t4', 404),
])
def test_track_view(app, tracks, track_id, format, expected_response, text_list):
    """
    Test the track view
    """
    url = '/track/{0}'.format(track_id)
    if format:
        url += '?format='+format
    response = app.get(url)
    assert response.status_code == expected_response
    for text in text_list:
        assert text.lower() in response.text.lower()

def test_track_list_all(app, tracks):
    response = app.get('/track_list')
    for text in ['track 1', 'track 2', 'track 3']:
        assert text in response.text

