## -*- coding: utf-8 -*-

import pytest

from ..model import init_DBSession, DBSession, commit
from ..model.init_data import init_data # humm ... could this be part of .model.__init__ ?

from ..model.model_tracks import Track, Tag, Attachment, Lyrics
from ..model.model_queue  import QueueItem
from ..model.actions import get_tag

import logging
log = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def test_db():
    """
    Setup DB
    """
    from pyramid.paster import get_appsettings, setup_logging
    #setup_logging(args.config_uri)
    #logging.basicConfig(level=logging.INFO)
    settings = get_appsettings('test.ini')
    init_DBSession(settings)
    init_data()
    return DBSession


@pytest.fixture(scope="module", params=[
    "mod1",
    "mod2",
])
def example(request):
    """
    Setup base test data for automated tests
    
    This should add the relevent data to an already blank database
    """
    param = request.param
    print("create {0}".format(param))
    print(param)
    def finalizer():
        print("finalizer {0}".format(param))
    request.addfinalizer(finalizer)
    return param
    


@pytest.fixture(scope="session")
def base_data(request, test_db):
    
    # Attachments --------------------------------------------------------------
    
    attachments_meta = [
        ('test/preview1.3gp' , 'preview'  ),
        ('test/preview2.flv' , 'preview'  ),        
        ('test/preview3.flv' , 'preview'  ),
        ('test/image1.jpg'   , 'thumbnail'),
        ('test/image2.jpg'   , 'thumbnail'),
        ('test/image3.png'   , 'thumbnail'),
        ('test/processed.mpg', 'video'    ),
        ('test/subtitles.ssa', 'subtitle' ),
    ]
    #attachments = []
    for location, type in attachments_meta:
        attachment = Attachment()
        attachment.location = location
        attachment.type     = type
        DBSession.add(attachment)
        #attachments.append(attachment)
    
    commit()

    def _get_attachment(filename):
        return DBSession.query(Attachment).filter(Attachment.location.like('%%{0}%%'.format(filename))).one()

    
    # Tags ---------------------------------------------------------------------
    
    # Series
    DBSession.add(Tag('series X', get_tag('from')))
    DBSession.add(Tag('series Y', get_tag('from')))
    DBSession.add(Tag('series Z', get_tag('from')))
    
    def _get_tag(tag):
        return get_tag(tag, create_if_missing=True)
    
    commit()
    
    # Tracks -------------------------------------------------------------------
    
    track = Track()
    track.id          = "t1"
    track.title       = "Test Track 1"
    track.description = "Test track for the KaraKara system with キ"
    track.duration    = 100
    [track.tags       .append(_get_tag       (t)) for t in ['opening','male','jp','anime','jpop', 'series X']]
    [track.attachments.append(_get_attachment(a)) for a in ['image1','preview1']]
    lyrics = Lyrics()
    lyrics.language = "jp"
    lyrics.content = "ここにいくつかのテキストです。"
    track.lyrics.append(lyrics)
    DBSession.add(lyrics)
    DBSession.add(track)
    
    track = Track()
    track.id          = "t2"
    track.title       = "Test Track 2"
    track.description = "Test track for the KaraKara system with キ"
    track.duration    = 200
    [track.tags       .append(_get_tag       (t)) for t in ['ending','female','en','anime', 'series X']]
    [track.attachments.append(_get_attachment(a)) for a in ['image2','preview2']]
    lyrics = Lyrics()
    lyrics.language = "en"
    lyrics.content = "Line1\nLine2\nLine3\nLine4\näöü"
    track.lyrics.append(lyrics)
    DBSession.add(lyrics)
    DBSession.add(track)
    
    track = Track()
    track.id          = "t3"
    track.title       = "Test Track 3"
    track.description = "Test track for the KaraKara system with キ"
    track.duration    = 300
    [track.tags       .append(_get_tag       (t)) for t in ['ending','female','en','anime', 'series Y']]
    [track.attachments.append(_get_attachment(a)) for a in ['image3','preview3']]
    DBSession.add(track)
    
    commit()
    
    def finalizer():
        print("finalizer for base_data")
    request.addfinalizer(finalizer)
