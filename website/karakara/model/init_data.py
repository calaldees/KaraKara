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
    
    log.info("Populating tables with base data")
    
    tags = []
    tags.append(Tag('anime'                           ))
    tags.append(Tag('series'                , tags[-1]))
    tags.append(Tag('opening'                         ))
    
    DBSession.add_all(tags)
    transaction.commit()  # Can't simply call DBSession.commit() as this is han handled my the Zope transcation manager .. wha?!
