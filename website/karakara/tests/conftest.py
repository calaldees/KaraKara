## -*- coding: utf-8 -*-

import pytest

from ..model import init_DBSession, DBSession, commit
from ..model.init_data import init_data

from ..model.model_tracks import Track, Tag, Attachment, Lyrics
from ..model.model_queue  import QueueItem
from ..model.actions import get_tag

import logging
log = logging.getLogger(__name__)




#ROOT_PATH = os.path.dirname(__file__)

def _pytest_sessionstart():
    # Only run database setup on master (in case of xdist/multiproc mode)
    if not hasattr(pytest.config, 'slaveinput'):
        from models import initialize_sql
        from pyramid.config import Configurator
        from paste.deploy.loadwsgi import appconfig
        from sqlalchemy import engine_from_config
        import os

        #ROOT_PATH = os.path.dirname(__file__)
        settings = appconfig('config:' + os.path.join(ROOT_PATH, 'test.ini'))
        engine = engine_from_config(settings, prefix='sqlalchemy.')

        print('Creating the tables on the test database {0}'.format(engine))

        config = Configurator(settings=settings)
        initialize_sql(settings, config)


@pytest.fixture(scope="session")
def test_db(request):
    """
    Setup DB
    """
    from pyramid.paster import get_appsettings, setup_logging
    #setup_logging(args.config_uri)
    #logging.basicConfig(level=logging.INFO)
    settings = get_appsettings('test.ini')
    init_DBSession(settings)
    init_data()
    
    def finalizer():
        print('finalze db')
        commit()
    request.addfinalizer(finalizer)
    
    return DBSession

#@pytest.fixture(scope="module", params=[
#    "mod1",
#    "mod2",
#])
#def example(request):
#    """
#    Setup base test data for automated tests
#    
#    This should add the relevent data to an already blank database
#    """
#    param = request.param
#    print("create {0}".format(param))
#    print(param)
#    def finalizer():
#        print("finalizer {0}".format(param))
#    request.addfinalizer(finalizer)
#    return param


@pytest.fixture(scope="session")
def tags(request, test_db):
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
        #(DBSession.delete(tag) for tag in tags)
        #commit()
        pass
    request.addfinalizer(finalizer)
    
    commit()
    return tags
    
    


@pytest.fixture(scope="session")
def attachments(request, test_db):
    """
    """
    attachments_data = [
        ('test/preview1.3gp' , 'preview'  ),
        ('test/preview2.flv' , 'preview'  ),        
        ('test/preview3.flv' , 'preview'  ),
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
        #(DBSession.delete(attachment) for attachment in attachments)
        #commit()
        print('finalze attach')
        pass
    request.addfinalizer(finalizer)
        
    commit()
    return attachments
    

@pytest.fixture(scope="session")
def lyrics(request, test_db):
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
        #(DBSession.delete(lyrics) for lyrics in lyrics_list)
        #commit()
        print('finalze lyrics')
        pass
    request.addfinalizer(finalizer)
    
    #commit()
    return lyrics_list


@pytest.fixture(scope="session")
def tracks(request, test_db, tags, attachments, lyrics):
    # = request.param
    tracks_data = [
        {
            'id'      :"t1",
            'duration': 100,
            'tags':[
                'title      :Test Track 1',
                'description:Test track for the KaraKara system with キ',
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
                'description:Test track for the KaraKara system with キ'
                'ending','female','en','anime', 'series X',
            ],
            'attachments': ['image2','preview2'],
            'lyrics':lyrics[1],
        },
        {
            'id'      :"t3",
            'duration': 300,
            'tags':[
                'title      :Test Track 3',
                'description:Test track for the KaraKara system with キ',
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
        #(DBSession.delete(track) for track in tracks)
        #commit()
        print('finalze tracks')
        pass
    request.addfinalizer(finalizer)
    
    commit()
    return tracks
