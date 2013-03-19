## -*- coding: utf-8 -*-

import pytest

# root catagory
# keywords
# trackids list passed

# search_tags
# search_list

# less than 15 tracks redirect view switch
# single view redirect to track view

@pytest.mark.parametrize(('url', 'expected_text', 'not_expected_text'), [
    ('/search_list/?trackids=t1,t2' , ['track 1', 'track 2']           , ['track 3', 'wildcard', 'ここ']),
    ('/search_list/?keywords=test'  , ['track 1', 'track 2', 'track 3'], ['wildcard']),
    ('/search_list/anime'           , ['track 1', 'track 2']           , ['wildcard', 'track 3']),
    ('/search_list/anime/en'        , ['track 2']                      , ['wildcard', 'track 1', 'track 3']),
    ('/search_list/jpop'            , ['track 3', 'track 1']           , ['wildcard', 'track 2']),
])
def test_track_list_tags(app, tracks, url, expected_text, not_expected_text):
    response = app.get(url)
    response_text = response.text.lower()
    for text in expected_text:
        assert text.lower() in response_text
    for not_text in not_expected_text:
        assert not_text not in response_text
