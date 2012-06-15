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