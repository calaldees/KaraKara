"""    
Sometimes we have a large global dataset of tracks.
An event may be run that resticts this global set to a subset of tracks.
e.g
  We may have 'rock', 'pop' and 'anime' tracks in our global dataset
  As this is used at an anime event, the audience may get frustrated
  with people selecting Nikelback or Rhinanna songs that are unrelated to the setting.

We can restrict tracks returned to a subset of tracks by enforcing
the 'karakara.search.tag.restrict' setting.
"""

from . import get_settings, temporary_setting


def test_search_tags_silent_forced(app, tracks, tracks_volume):
    assert not get_settings(app)['karakara.search.tag.silent_forced']
    assert not get_settings(app)['karakara.search.tag.silent_hidden']
    
    data = app.get('/search_list/.json').json['data']
    assert len(data['trackids']) == 19
    
    # Test silent_forced - restrict down to 'category:anime' tracks
    #  - t1 and t2 are the only two tracks tags as anime
    with temporary_setting(app, 'karakara.search.tag.silent_forced', 'category:anime'):
        assert get_settings(app)['karakara.search.tag.silent_forced'] == 'category:anime'
        data = app.get('/search_list/.json').json['data']
        assert len(data['trackids']) == 2
        assert 't1' in data['trackids']

    # Test silent_hidden - hide tracks with tag 'category:anime'
    #  - t1 and t2 are the only two tracks tags as anime they should be hidden in the response
    with temporary_setting(app, 'karakara.search.tag.silent_hidden', 'category:anime'):
        assert get_settings(app)['karakara.search.tag.silent_hidden'] == 'category:anime'
        data = app.get('/search_list/.json').json['data']
        assert len(data['trackids']) == 17
        assert 't1' not in data['trackids']

    assert not get_settings(app)['karakara.search.tag.silent_forced']
    assert not get_settings(app)['karakara.search.tag.silent_hidden']
