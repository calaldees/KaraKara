import os

import logging
log = logging.getLogger(__name__)


version = "0.0"



#-------------------------------------------------------------------------------
# Import from URL
#-------------------------------------------------------------------------------
def walk_url(uri):
    print("walk url not implemented yet")


#-------------------------------------------------------------------------------
# Import from local filesystem
#-------------------------------------------------------------------------------
def walk_local(uri):
    for root, dirs, files in os.walk(uri):
       for name in files:
           filename = os.path.join(root, name)
           print(filename)


#-------------------------------------------------------------------------------
# Process JSON leaf
#-------------------------------------------------------------------------------
def import_json_data(json_source, root_path):
    """
    source should be a filetype object for a json file to import
    it shouldnt be relevent that it is local or remote
    """
    pass


#-------------------------------------------------------------------------------
# Import - URI crawl method selector
#-------------------------------------------------------------------------------

def import_media(uri):
    """
    Recursivly traverse uri location searching for .json files to import
    should be able to traverse local file system and urls
    """
    if (uri.startswith('http')):
        walk_url(uri)
    else:
        walk_local(uri)


#-------------------------------------------------------------------------------
# Command Line
#-------------------------------------------------------------------------------

def get_args():
    import argparse
    # Command line argument handling
    parser = argparse.ArgumentParser(
        description="""Import media to local Db""",
        epilog=""""""
    )
    parser.add_argument('source_uri'  , help='uri of track media data')
    parser.add_argument('--config_uri', help='config .ini file for logging configuration')
    parser.add_argument('--version', action='version', version=version)

    return parser.parse_args()

def main():
    args = get_args()
    
    if args.config_uri:
        # Setup Logging and import Settings
        from pyramid.paster import setup_logging
        setup_logging(args.config_uri)
    
    import_media(args.source_uri)
    
    
if __name__ == "__main__":
    main()