## -*- coding: utf-8 -*-

import pytest

from karakara.model.actions import get_tag
from karakara.model.model_tracks import Track, Tag, Attachment, Lyrics


@pytest.fixture(scope="session")
def tags(request, DBSession, commit):
    """
    """
    tags_data = [
        'from:series X',
        'from:series Y',
        'from:series Z',
    ]
    tags = []
    for tag_data in tags_data:
        tag = get_tag(tag_data, create_if_missing=True)#Tag(tag_data, create_if_missing=True)
        DBSession.add(tag)
        tags.append(tag)
    
    def finalizer():
        pass
        #for tag in tags:
        #    DBSession.delete(tag)
        #commit()
    #request.addfinalizer(finalizer)
    
    commit()
    return tags
    

@pytest.fixture(scope="session")
def attachments(request, DBSession, commit):
    """
    """
    attachments_data = [
        ('test/preview1.3gp' , 'preview'  ),
        ('test/preview2.flv' , 'preview'  ),        
        ('test/preview3.mp4' , 'preview'  ),
        ('test/image1.jpg'   , 'thumbnail'),
        ('test/image2.jpg'   , 'thumbnail'),
        ('test/image3.png'   , 'thumbnail'),
        ('test/processed.mpg', 'video'    ),
        ('test/subtitles.ssa', 'subtitle' ),
    ]
    attachments = []
    for attachment_location, attachment_type in attachments_data:
        attachment = Attachment()
        attachment.location = attachment_location
        attachment.type     = attachment_type
        DBSession.add(attachment)
        attachments.append(attachment)
    
    def finalizer():
        for attachment in attachments:
            DBSession.delete(attachment)
        commit()
    request.addfinalizer(finalizer)
        
    commit()
    return attachments
    

@pytest.fixture(scope="session")
def lyrics(request, DBSession, commit):
    lyrics_data = [
        {
            'language':'jp',
            'content' :'ここにいくつかのテキストです。',
        },
        {
            'language':'en',
            'content' :'Line1\nLine2\nLine3\nLine4\näöü"',
        },
    ]
    lyrics_list = []
    for lyric_data in lyrics_data:
        lyrics = Lyrics()
        for k,v in lyric_data.items():
            setattr(lyrics,k,v)
        #DBSession.add(lyrics)
        lyrics_list.append(lyrics)
    
    def finalizer():
        pass
        #for lyrics in lyrics_list:
        #    DBSession.delete(lyrics)
        #commit()
    request.addfinalizer(finalizer)
    
    #commit()
    return lyrics_list


@pytest.fixture(scope="session")
def tracks(request, DBSession, commit, tags, attachments, lyrics):
    tracks_data = [
        {
            'id'      :"t1",
            'duration': 100,
            'tags':[
                'title      :Test Track 1',
                #'description:Test track for the KaraKara system with キ',
                'opening','male','jp','anime','jpop', 'series X',
            ],
            'attachments': ['image1','preview1'],
            'lyrics': lyrics[0],
        },
        {
            'id'      :"t2",
            'duration': 200,
            'tags':[
                'title      :Test Track 2',
                #'description:Test track for the KaraKara system with キ'
                'ending','female','en','anime', 'series X',
            ],
            'attachments': ['image2','preview2'],
            'lyrics':lyrics[1],
        },
        {
            'id'      :"t3",
            'duration': 300,
            'tags':[
                'title      :Test Track 3 キ',
                #'description:Test track for the KaraKara system with キ',
                'ending','female','en','anime', 'series Y',
            ],
            'attachments': ['image3','preview3'],
        },
    ]

    def _get_tag(tag):
        return get_tag(tag, create_if_missing=True)    
    def _get_attachment(filename):
        return DBSession.query(Attachment).filter(Attachment.location.like('%%{0}%%'.format(filename))).one()
    
    tracks = [] # Keep tabs on all tracks generated 
    for track_data in tracks_data:
        track = Track()
        track.id          = track_data['id']
        track.duration    = track_data['duration']
        [track.tags       .append(_get_tag       (t)) for t in track_data['tags']       ]
        [track.attachments.append(_get_attachment(a)) for a in track_data['attachments']]
        if 'lyrics' in track_data:
            track.lyrics.append(track_data['lyrics'])
        DBSession.add(track)
        tracks.append(track)

    def finalizer():
        pass
        #for track in tracks:
        #    DBSession.delete(track)
        #commit()
    request.addfinalizer(finalizer)
    
    commit()
    return tracks
