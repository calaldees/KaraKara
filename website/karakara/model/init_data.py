from . import DBSession, init_db
import transaction

import logging
log = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
# DB Objects
#-------------------------------------------------------------------------------

from .model_tracks import Track, Tag
from .model_queue  import QueueItem

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
    
    DBSession.add_all(tags)
    transaction.commit()
    
    track1 = Track()
    track1.id          = "t1"
    track1.title       = "Test Track"
    track1.description = "Test track description"
    track1.duration    = 120
    track1.tags        = tags
    
    DBSession.add(track1)
    transaction.commit() # Can't simply call DBSession.commit() as this is han handled my the Zope transcation manager .. wha?!

