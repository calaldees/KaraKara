## -*- coding: utf-8 -*-

import pytest

# root catagory
# keywords
# trackids list passed

# search_tags
# search_list

def test_track_list(app, tracks):
    response = app.get('/search_list/?trackids=t1,t2')
    response_text = response.text.lower()
    for track_title in ['track 1', 'track 2']:
        assert track_title.lower() in response_text
    assert 'track 3' not in response_text
    
def test_track_list(app, tracks):
    response = app.get('/search_list/?keywords=test')
    response_text = response.text.lower()
    for track_title in ['track 1', 'track 2', 'track 3']:
        assert track_title.lower() in response_text
    assert 'wildcard' not in response_text