## -*- coding: utf-8 -*-

import pytest

@pytest.mark.parametrize(('track_id', 'expected_response', 'text_list',), [
    ('t1', 200, ['Test track 1'   , 'series x', 'anime', 'ここ', 'test/image1.jpg'  ]),
    ('t2', 200, ['Test track 2'   , 'series x', 'anime', 'äöü', 'test/preview2.flv']),
    ('t3', 200, ['Test track 3 キ', 'series y', 'anime',        'test/preview3.mp4']),
    #('t4', 404),
])
def test_track_view(app, tracks, track_id, expected_response, text_list):
    response = app.get('/track/{0}'.format(track_id))
    assert response.status_code == expected_response
    for text in text_list:
        assert text in response.text