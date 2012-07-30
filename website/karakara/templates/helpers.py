from ..lib.misc import get_fileext

import random

import logging
log = logging.getLogger(__name__)


video_fileext_to_mime_types = {
    'mp4':'mp4' ,
    'ogv':'ogg' ,
    'mpg':'mpeg',
    '3gp':'3gp' ,
    '???':'webm',
    'mov':'quicktime',
    'mkv':'x-matroska',
    'wmv':'x-ms-wmv',
    'flv':'x-flv',
}


def media_url(file):
    #return '/media/%s' % file
    return '/files/%s' % file

def track_url(id):
    return '/track/%s' % id

def search_url(tags=[],route='search_tags', **kwargs):
    route_path = "/%s/%s" % (route, "/".join(tags))
    if kwargs:
        route_path += '?' + '&'.join(["%s=%s"%(key,",".join(items)) for key, items in kwargs.items()])
    return route_path

def duration_str(duration):
    """
    duration in seconds to human readable string form
    """
    return "%d min" % (duration/60)
    
def attachment_locations_by_type(track, attachment_type):
    return [media_url(attatchment['location']) for attatchment in track['attachments'] if attatchment['type']==attachment_type]

def thumbnail_location_from_track(track, index=0):
    thumbnails = attachment_locations_by_type(track,'thumbnail')
    if not thumbnails:
        return
    if index=='random':
        index = random.randint(0,thumbnails.length)
    return thumbnails[index]

def video_mime_type(attachment):
    return video_fileext_to_mime_types.get(get_fileext(attachment['location']),'mp4')

title_tags_for_category = {
    'DEFAULT':['from','use','title','length','lang'],
    'jpop'   :['artist','title'],
    'meme'   :['title','from'],
}
def track_title(tags, exclude_tags=[]):
    exclude_tags = [tag.split(':')[0] for tag in exclude_tags]
    if tags.get('title')==tags.get('from'):
        exclude_tags.append('title')
    title_tags   = title_tags_for_category.get(tags.get('category','DEFAULT'), title_tags_for_category['DEFAULT'])
    tags_to_use  = [tag for tag in title_tags if tag not in exclude_tags]
    return " - ".join([t for t in [tags.get(tag_to_use,'') for tag_to_use in tags_to_use] if t])

def track_title_only(track):
    title = track.get('title')
    for tag in ['title','from','artist']:
        try:
            title = track['tags'][tag]
            break
        except: pass
    return title.capitalize()