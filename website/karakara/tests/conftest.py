## -*- coding: utf-8 -*-

import pytest

from ..model import DBSession, commit

from ..model.actions import get_tag
from ..model.model_tracks import Track, Tag, Attachment
from ..model.model_queue  import QueueItem

import logging
log = logging.getLogger(__name__)



    
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
    

def get_attachment(filename):
    return DBSession.query(Attachment).filter(Attachment.location.like('%%{0}%%'.format(filename))).one()


def init_base_data():
    
    # Attachments --------------------------------------------------------------
    
    attachments_meta = [
        ('test/preview1.3gp' , 'preview'  ),
        ('test/preview2.flv' , 'preview'  ),        
        ('test/preview3.flv' , 'preview'  ),
        ('test/image1.jpg'   , 'image'    ),
        ('test/image2.jpg'   , 'image'    ),
        ('test/image3.png'   , 'image'    ),
        ('test/processed.mpg', 'processed'),
        ('test/subtitles.ssa', 'subtitle' ),
    ]
    attachments = []
    for location, type in attachments_meta:
        attachment = Attachment()
        attachment.location = location
        attachment.type     = type
        DBSession.add(attachment)
        attachments.append(attachment)
    
    commit()
    
    # Tags ---------------------------------------------------------------------
    
    # Series
    DBSession.add(Tag('series X', get_tag('from')))
    DBSession.add(Tag('series Y', get_tag('from')))
    DBSession.add(Tag('series Z', get_tag('from')))
    
    commit()
    
    # Tracks -------------------------------------------------------------------
    
    track = Track()
    track.id          = "t1"
    track.title       = "Test Track 1"
    track.description = "Test track for the KaraKara system with キ"
    track.duration    = 100
    track.tags        = [get_tag(t)        for t in ['opening','male','jp','anime','jpop', 'series X']]
    track.attachments = [get_attachment(a) for a in ['image1','preview1']]
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
    track.tags        = [get_tag(t)        for t in ['ending','female','en','anime', 'series X']]
    track.attachments = [get_attachment(a) for a in ['image2','preview2']]
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
    track.tags        = [get_tag(t)        for t in ['ending','female','en','anime', 'series Y']]
    track.attachments = [get_attachment(a) for a in ['image3','preview3']]
    DBSession.add(track)
    
    commit()
    