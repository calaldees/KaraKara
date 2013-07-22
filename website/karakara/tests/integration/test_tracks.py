## -*- coding: utf-8 -*-

import pytest

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

def test_track_view_api(app, tracks):
    """
    Track's can be returned as structured JSON data
    Lightly touch the structure and test correct unicode throughput
    """
    data = app.get('/track/t1?format=json').json['data']
    assert data['track']['id'] == 't1'
    assert 'ここ' in data['track']['lyrics'][0]['content']
    
def test_track_list_all(app, tracks):
    """
    Track list displays all tracks in one giant document
    Used for printing
    """
    response = app.get('/track_list')
    for text in ['track 1', 'track 2', 'track 3', 'wildcard']:
        assert text in response.text

def test_track_list_all_api(app, tracks):
    data = app.get('/track_list?format=json').json['data']
    assert 'test track 2' in [title for track in data['list'] for title in track['tags']['title']]

def test_track_list_all(app):
    """
    Uknown track
    """
    response = app.get('/track/unknown_track_id', expect_errors=True)
    assert response.status_code == 404
