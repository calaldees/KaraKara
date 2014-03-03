import os
import json
import urllib
import re
import hashlib

from bs4 import BeautifulSoup
import traceback

from externals.lib.misc import get_fileext, random_string

from ..model.model_tracks import Track, Tag, Attachment, Lyrics, _attachment_types

from ..model         import init_DBSession, DBSession, commit
from ..model.actions import get_tag

import logging
log = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------

version = "0.0"

file_component_separator = r'[ .\\/\[\]]'

def sep(text):
    return r'%s%s\d?%s' % (file_component_separator, text, file_component_separator)
def or_sep(*args):
    return r'|'.join(args)

tag_extractors = {
    'opening' : re.compile(or_sep('open','intro','opening','op'), re.IGNORECASE),
    'ending'  : re.compile(or_sep('end' ,'outro','ending' ,'ed'), re.IGNORECASE),
    'anime'   : re.compile(r'anime', re.IGNORECASE),
}

#skippy = 'string in filename to skip to'

#-------------------------------------------------------------------------------
# Import from URL
#-------------------------------------------------------------------------------
def walk_url(uri):
    webpage = urllib.request.urlopen(uri)
    soup = BeautifulSoup(webpage.read())
    webpage.close()
    for href in [link.get('href') for link in soup.find_all('a')]:
        if href.endswith('/'):
            log.warn("directory crawling from urls is not implmented yet: %s" % href)
        elif href.endswith('.json'):
            absolute_filename = uri + href #AllanC - todo - this is not absolute if dir's are crawled!
            with urllib.request.urlopen(absolute_filename) as file:
                import_json_data(file, absolute_filename)


#-------------------------------------------------------------------------------
# Import from local filesystem
#-------------------------------------------------------------------------------
def walk_local(uri):
    for root, dirs, files in os.walk(uri):
        for json_filename in [f for f in files if get_fileext(f)=='json']:
            absolute_filename = os.path.join(root         , json_filename)
            #relative_path = root.replace(uri,'')
            #relative_filename = os.path.join(relative_path, json_filename)
            with open(absolute_filename, 'r') as file:
                import_json_data(file, absolute_filename)


#-------------------------------------------------------------------------------
# Process JSON leaf
#-------------------------------------------------------------------------------
def import_json_data(source, location=''):
    """
    source should be a filetype object for a json file to import
    it shouldnt be relevent that it is local or remote
    """
    
    def gen_id_for_track(track):
        """
        TODO: This method is a hecky peice of crap ... I feel dirty just looking at it.
        The hash generation is particulaly horrible.
        I would suggest some tidying
        """
        id = ''
        
        # Gen 3 letter ID from category,from,title
        def get_chars(s, num=2):
            try:
                return re.search(r'(\w{%s})'% num, s.replace(' ','')).group(1)
            except:
                return ''

        # sprinkle on a little bit of 'title' hashy goodness in the hope that we wont get colisions
        exclude_tags = ('status:', '#')
        identifyer_string = "-".join(filter(lambda tag: not any((exclude_tag in tag for exclude_tag in exclude_tags  )) ,sorted(tag.full for tag in track.tags)))
        try:
            title_hash = re.search(r'([1-9][abcdef123456789])', hashlib.sha1(identifyer_string.encode('utf-8')).hexdigest().lower()).group(1) #hex(hash(
        except Exception:
            title_hash = ''
        
        _get_chars = lambda parent, num: get_chars(track.get_tag(parent), num)
        id = "".join((
            _get_chars('category', 1),
            _get_chars('from', 2) or _get_chars('artist', 2) ,
            _get_chars('title', 2),
            title_hash,
        ))
        
        # If the tags were not present; then split the title string and get the first 3 characters
        if not id:
            log.error('unable to aquire id from tags - uing random id')
            id = random_string(length=5)
        
        # Normaize case
        id = id.lower()
        
        # Check for colistions and make unique number
        def get_id_number(id):
            count = 0
            def get_count():
                return str(count) if count else ''
            while DBSession.query(Track).filter_by(id=id+get_count()).count():
                count += 1
                log.warn('track.id colision - this is unexpected and could lead to inconsistencys with track naming for printed lists in the future {0}, press c to continue'.format(id))
                import pdb ; pdb.set_trace()
            return get_count()
        id += get_id_number(id)
        
        return id
    
    
    def get_data():
        try:
            if hasattr(source,'read'):
                data = source.read()
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            return json.loads(data)
        except Exception as e:
            log.warn('Failed to process %s' % location)
            traceback.print_exc()
    
    data = get_data()
    if not data:
        return
    
    # AllanC - useful code to skip to a particular track in processing - i've needed it a couple if times so just leaving it here.
    #global skippy
    #if skippy:
    #    if skippy not in location: return
    #    skippy = False
    
    if 'description.json' in location:
        try:
            folder = data['name']
            log.info('Importing %s' % folder)
            
            track = Track()
            #track.id       = get_id_from_foldername(folder)#data['videos'][0]['encode-hash']
            track.source   = ''
            track.duration = data['videos'][0]['length']
            #track.title    = data['name']
            
            # Add Attachments
            for attachment_type in _attachment_types.enums:
                for attachment_data in data.get("%ss"%attachment_type,[]):
                    attachment = Attachment()
                    attachment.type     = attachment_type
                    attachment.location = os.path.join(folder,  attachment_data.get('url'))
                    
                    extra_fields = {}
                    for key,value in attachment_data.items():
                        if key in ['target','vcodec']:
                            #print ("%s %s" % (key,value))
                            extra_fields[key] = value
                    attachment.extra_fields = extra_fields
                    
                    track.attachments.append(attachment)
            
            # Add Lyrics
            for subtitle in data.get('subtitles',[]):
                lyrics = Lyrics()
                lyrics.language = subtitle.get('language','eng')
                lyrics.content  = "\n".join(subtitle.get('lines',[]))
                track.lyrics.append(lyrics)
            
            # Import tags.txt
            try:
                with open(os.path.join(os.path.dirname(location),'tags.txt'), 'r') as tag_file:
                    for tag_string in tag_file:
                        tag_string = tag_string.strip()
                        tag = get_tag(tag_string, create_if_missing=True) 
                        if tag:
                            track.tags.append(tag)
                        elif tag_string:
                            log.warn('%s: null tag "%s"' % (location, tag_string))
            except Exception as e:
                log.warn('Unable to imports tags')
                #traceback.print_exc()
                #exit()
            
            for duplicate_tag in [tag for tag in track.tags if track.tags.count(tag) > 1]:
                log.warn('Unneeded duplicate tag found %s in %s' %(duplicate_tag, location))
                track.tags.remove(duplicate_tag)
            
            # AllanC TODO: if there is a duplicate track.id we may still want to re-add the attachments rather than fail the track entirely
            
            # Finally, use the tags to make a unique id for this track
            track.id = gen_id_for_track(track)
            
            DBSession.add(track)
            commit()
        except Exception as e:
            log.warn('Unable to process %s because %s' % (location, e))
            traceback.print_exc()
            #exit()


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
    parser.add_argument('--config_uri', help='config .ini file for logging configuration', default='development.ini')
    parser.add_argument('--version', action='version', version=version)

    return parser.parse_args()

def main():
    args = get_args()
    
    # Setup Logging and Db from .ini
    from pyramid.paster import get_appsettings, setup_logging
    #setup_logging(args.config_uri)
    logging.basicConfig(level=logging.INFO)
    settings = get_appsettings(args.config_uri)
    init_DBSession(settings)
    
    log.info('Importing tracks from {0}'.format(args.source_uri))
    import_media(args.source_uri)
    
    
if __name__ == "__main__":
    main()
