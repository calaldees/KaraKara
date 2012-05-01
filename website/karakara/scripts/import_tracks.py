import os
import json
import urllib
import re
import io
from bs4 import BeautifulSoup

from ..lib.misc import get_fileext

import logging
log = logging.getLogger(__name__)


version = "0.0"



#-------------------------------------------------------------------------------
# Import from URL
#-------------------------------------------------------------------------------
def walk_url(uri):
    webpage = urllib.request.urlopen(uri)
    soup = BeautifulSoup(webpage.read())
    webpage.close()
    for href in [link.get('href') for link in soup.find_all('a')] :
        if href.endswith('/'):
            print("dir %s" % href)
        elif href.endswith('.json'):
            with urllib.request.urlopen(uri+href) as file:
                import_json_data(file.read().decode('utf-8'), uri)
                
    

#-------------------------------------------------------------------------------
# Import from local filesystem
#-------------------------------------------------------------------------------
def walk_local(uri):
    for root, dirs, files in os.walk(uri):
        for json_filename in [f for f in files if get_fileext(f)=='json']:
            relative_path = root.replace(uri,'')
            absolute_filename = os.path.join(root         , json_filename)
            relative_filename = os.path.join(relative_path, json_filename)
            log.debug(relative_filename)
            with open(absolute_filename, 'r') as file:
                import_json_data(file, relative_path)


#-------------------------------------------------------------------------------
# Process JSON leaf
#-------------------------------------------------------------------------------
def import_json_data(json_source, root_path):
    """
    source should be a filetype object for a json file to import
    it shouldnt be relevent that it is local or remote
    """
    if isinstance(json_source, io.IOBase):
        data = json.load(json_source)
    elif isinstance(json_source, str):
        data = json.loads(json_source)
    else:
        raise Exception("unknown json_source type")
    print(data)


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