## -*- coding: utf-8 -*-

import pytest

from . import admin_rights


@pytest.mark.parametrize(('track_id', 'expected_response', 'text_list',), [
    ('t1', 200, ['Test Track 1'   , 'series X', 'anime', 'ここ', 'test/image1.jpg'  ]),
    ('t2', 200, ['Test Track 2'   , 'series X', 'anime', 'äöü', 'test/preview2.flv']),
    ('t3', 200, ['Test Track 3 キ', 'series Y', 'jpop' ,        'test/preview3.mp4']),
    #('t4', 404),
])
def test_track_view(app, tracks, track_id, expected_response, text_list):
    """
    Test the track html view
    Assert the track data is rendered by the template 
    """
    url = '/track/{0}'.format(track_id)
    response = app.get(url)
    assert response.status_code == expected_response
    for text in text_list:
        assert text.lower() in response.text.lower()
    assert 'poster="/files/test/image' in response.text, 'html5 video poster with an image should be present'


def test_track_view_api(app, tracks):
    """
    Track's can be returned as structured JSON data
    Lightly touch the structure and test correct unicode throughput
    """
    data = app.get('/track/t1?format=json').json['data']
    assert data['track']['id'] == 't1'
    assert 'ここ' in data['track']['lyrics']


def test_track_list_print_all(app, tracks):
    """
    Track list displays all tracks in one giant document
    Used for printing
    """
    with admin_rights(app):
        response = app.get('/track_list')
        for text in ['track 1', 'track 2', 'track 3', 'wildcard']:
            assert text in response.text


def test_track_list_print_all_api(app, tracks):
    # TODO: Security has been disbaled temporerally. This should be re-enabled ASAP
    #assert app.get('/track_list.json', expect_errors=True).status_code == 403
    with admin_rights(app):
        data = app.get('/track_list?format=json').json['data']
        assert 'test track 2' in [title for track in data['list'] for title in track['tags']['title']]


def test_track_unknown(app):
    """
    Uknown track
    """
    response = app.get('/track/unknown_track_id', expect_errors=True)
    assert response.status_code == 404


def test_track_list(app, tracks):
    """
    Because we have so few tracks in the test database - search_list should r
    eturn ALL the tracks in an html list. The thumbnails should be present for each track
    """
    response = app.get('/search_list/')
    for text in ('Test Track 1', 'Test Track 2', 'Test Track 3 キ', 'Wildcard', 'test/image1.jpg', 'test/image2.jpg'):
        assert text in response.text
    for text in ('test/preview1.3gp', ):
        assert text not in response.text
