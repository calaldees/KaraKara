

import logging
log = logging.getLogger(__name__)


video_files = [
    ('.mp4','mp4'),
    ('.ogv','ogg'),
    ('.mpg','mpg'),
    ('.3gp','3gp'),
]


def media_url(file):
    return '/media/%s' % file

def track_url(id):
    return '/track/%s' % id

def duration_str(duration):
    """
    duration in seconds to human readable string form
    """
    return "%d min" % (duration/60)
    
