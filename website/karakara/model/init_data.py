"""
Init KaraKara base tables
This should by convention be separate to the DBSession as this imports Model objects
and therefore binding to Base
"""

from . import DBSession, init_db, commit


import logging
log = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
# DB Objects
#-------------------------------------------------------------------------------

# The DB modules imported here will be created as part of the blank database.
# If you add a new model ensure it ia added here
from .model_tracks   import Track, Tag
from .model_queue    import QueueItem
from .model_feedback import Feedback
from .model_token    import PriorityToken

# db action import
from .actions import get_tag

#-------------------------------------------------------------------------------
# Init Base Data
#-------------------------------------------------------------------------------

def init_data():
    init_db() # Clear current DB and Create Blank Tables
    
    log.info("Populating tables with base data")
    
    base_tags = [
        'category:anime',
        'category:jdrama',
        'category:jpop',
        'category:cartoon',
        'category:tokusatsu',
        'category:musical',
        'category:game',
        'category:meme',
        'from',
        'title',
        'description',
        'lang:en',
        'lang:jp',
        'lang:ln',
        'lang:fr',
        'artist',
        'vocalstyle:female',
        'vocalstyle:male',
        'vocalstyle:duet',
        'vocalstyle:group',
        'vocalstyle:backing',
        'vocaltrack:on',
        'vocaltrack:off',
        'vocaltrack:band',
        'length:full',
        'length:short',
        'use:opening',
        'use:ending',
        'use:ost',
        'use:insert',
        'use:image',
        'use:op',
        'use:ed',
        'use:op1',
        'use:op2',
        'use:op3',
        'use:op4',
        'use:op5',
        'use:op6',
        'use:op7',
        'use:op8',
        'use:op9',
        'use:ed1',
        'use:ed2',
        'use:ed3',
        'use:ed4',
        'use:ed5',
        'use:ed6',
        'use:ed7',
        'use:ed8',
        'use:ed9',
    ]
    
    for tag in base_tags:
        get_tag(tag, create_if_missing=True)
    
    #DBSession.add_all(tags)
    commit()  # Can't simply call DBSession.commit() as this is han handled my the Zope transcation manager .. wha?!

    