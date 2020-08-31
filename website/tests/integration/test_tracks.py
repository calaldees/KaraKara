## -*- coding: utf-8 -*-

import pytest

from . import admin_rights


@pytest.mark.parametrize(('track_id', 'expected_response', 'text_list',), [
    ('t1', 200, ['Test Track 1'   , 'series X', 'anime', 'ここ', 'test/image1.jpg'  ]),
    ('t2', 200, ['Test Track 2'   , 'series X', 'anime', 'äöü', 'test/preview2.flv']),
    ('t3', 200, ['Test Track 3 キ', 'series Y', 'jpop' ,        'test/preview3.mp4']),
    #('t4', 404),
])
def test_track_view(app, queue, tracks, track_id, expected_response, text_list):
    """
    Test the track html view
    Assert the track data is rendered by the template
    """
    url = f'/queue/{queue}/track/{track_id}'
    response = app.get(url)
    assert response.status_code == expected_response
    for text in text_list:
        assert text.lower() in response.text.lower()
    assert 'poster="/files/test/image' in response.text, 'html5 video poster with an image should be present'


def test_track_view_api(app, queue, tracks):
    """
    Track's can be returned as structured JSON data
    Lightly touch the structure and test correct unicode throughput
    """
    data = app.get(f'/queue/{queue}/track/t1?format=json').json['data']
    assert data['track']['id'] == 't1'
    assert 'ここ' in data['track']['srt']


def test_track_unknown(app, queue):
    """
    Uknown track
    """
    response = app.get(f'/queue/{queue}/track/unknown_track_id', expect_errors=True)
    assert response.status_code == 404


def test_track_redirect_query_string(app, queue):
    """
    Track redirect id
    """
    response = app.get(f'/queue/{queue}/track?track_id=t1')
    assert response.status_code == 302
    response = response.follow()
    assert response.status_code == 200
    assert 'Test Track 1' in response.text


def test_track_redirect_partial(app, queue):
    """
    Track redirect partial id
    """
    response = app.get(f'/queue/{queue}/track/x')
    assert response.status_code == 302
    response = response.follow()
    assert response.status_code == 200
    assert 'Wildcard' in response.text


def test_track_list(app, tracks, queue):
    """
    Because we have so few tracks in the test database - search_list should
    return ALL the tracks in an html list. The thumbnails should be present
    for each track
    """
    response = app.get(f'/queue/{queue}/search_list/')
    for text in (
        'Test Track 1',
        'Test Track 2',
        'Test Track 3 キ',
        'Wildcard',
        'test/image1.jpg',
        'test/image2.jpg',
        f'/queue/{queue}/track/t1',
    ):
        assert text in response.text
    for text in ('test/preview1.3gp', ):
        assert text not in response.text
