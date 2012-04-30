from .models import DBSession, init_DBSession, init_db

from .model_tracks import Track, Tag
from .model_queue  import QueueItem

import logging
log = logging.getLogger(__name__)

import transaction

version = "0.0"

#-------------------------------------------------------------------------------
# Init Base Data
#-------------------------------------------------------------------------------

def init_base_data():
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


#-------------------------------------------------------------------------------
# Command Line
#-------------------------------------------------------------------------------

def get_args():
    import argparse
    # Command line argument handling
    parser = argparse.ArgumentParser(
        description="""Init database""",
        epilog=""""""
    )
    parser.add_argument('--version', action='version', version=version)
    parser.add_argument('config_uri', help='config .ini uri')

    return parser.parse_args()

def main():
    args = get_args()
    
    # Setup Logging and import Settings
    from pyramid.paster import get_appsettings, setup_logging
    setup_logging(args.config_uri)
    settings = get_appsettings(args.config_uri)
    
    # Setup DB
    init_DBSession(settings) # Connect to DBSession
    init_base_data()         # Populate base data
    
if __name__ == "__main__":
    main()