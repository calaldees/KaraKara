"""
Sometimes we have a large global dataset of tracks.
An event may be run that restricts this global set to a subset of tracks.
e.g
  We may have 'rock', 'pop' and 'anime' tracks in our global dataset
  As this is used at an anime event, the audience may get frustrated
  with people selecting Nikelback or Rhinanna songs that are unrelated to the setting.

We can restrict tracks returned to a subset of tracks by enforcing
the 'karakara.search.tag.restrict' setting.
"""
from unittest.mock import patch
import bs4
def BeautifulSoup(markup):
    return bs4.BeautifulSoup(markup, "html.parser")


from . import admin_rights, temporary_settings


def test_search_tags_silent_forced(app, queue, tracks, tracks_volume):
    def get_settings():
        return app.get(f'/queue/{queue}/settings.json').json['data']['settings']
    settings = get_settings()
    assert settings['karakara.search.tag.silent_forced'] == []
    assert settings['karakara.search.tag.silent_hidden'] == []

    def get_search_list_data():
        return app.get(f'/queue/{queue}/search_list/.json').json['data']

    data = get_search_list_data()
    assert len(data['trackids']) == 19

    # Test silent_forced - restrict down to 'category:anime' tracks
    #  - t1 and t2 are the only two tracks tags as anime
    #with patch.dict(settings, {'karakara.search.tag.silent_forced': ['category:anime']}):
    with temporary_settings(app, queue, {'karakara.search.tag.silent_forced': ['category:anime']}):
        assert get_settings()['karakara.search.tag.silent_forced'] == ['category:anime']
        data = get_search_list_data()
        assert len(data['trackids']) == 2
        assert 't1' in data['trackids']

    # Test silent_hidden - hide tracks with tag 'category:anime'
    #  - t1 and t2 are the only two tracks tags as anime they should be hidden in the response
    #with patch.dict(settings, {'karakara.search.tag.silent_hidden': ['category:anime']}):
    with temporary_settings(app, queue, {'karakara.search.tag.silent_hidden': ['category:anime']}):
        assert get_settings()['karakara.search.tag.silent_hidden'] == ['category:anime']
        data = get_search_list_data()
        assert len(data['trackids']) == 17
        assert 't1' not in data['trackids']

    settings = get_settings()
    assert not settings['karakara.search.tag.silent_forced']
    assert not settings['karakara.search.tag.silent_hidden']
