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

from . import setting

@setting(key='karakara.search.tag.restrict', value='category:anime')
def test_search_tags_restrict(app, tracks, tracks_volume): #, search_tags, expected_tag_set
    #assert False
    pass
