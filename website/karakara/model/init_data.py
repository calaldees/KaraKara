from . import DBSession, init_db
import transaction

import logging
log = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
# DB Objects
#-------------------------------------------------------------------------------

from .model_tracks import Track, Tag
from .model_queue  import QueueItem

# db action import
from .actions import get_tag

#-------------------------------------------------------------------------------
# Init Base Data
#-------------------------------------------------------------------------------

def init_data():
    init_db() # Clear current DB and Create Blank Tables
    
    log.info("Populating tables with base test data")
    
    tags = []
    tags.append(Tag('anime'                           ))
    tags.append(Tag('series'                , tags[-1]))
    tags.append(Tag('fist of the north star', tags[-1]))
    tags.append(Tag('opening'                         ))
    
    DBSession.add_all(tags)
    transaction.commit()
    
    track1 = Track()
    track1.id          = "track1"
    track1.title       = "Test Track 1"
    track1.description = "Test track description"
    track1.duration    = 120
    track1.tags        = tags
    DBSession.add(track1)
    
    transaction.commit() # Can't simply call DBSession.commit() as this is han handled my the Zope transcation manager .. wha?!
    
    
    track2 = Track()
    track2.id          = "track2"
    track2.title       = "Test Track 2"
    track2.description = "Test track description"
    track2.duration    = 240
    track2.tags.append(get_tag('anime'))
    track2.tags.append(get_tag('opening'))
    DBSession.add(track2)

    track3 = Track()
    track3.id          = "track3"
    track3.title       = "Test Track 3"
    track3.description = "Test track description"
    track3.duration    = 360
    track3.tags.append(get_tag('anime'))
    DBSession.add(track3)
    
    transaction.commit()