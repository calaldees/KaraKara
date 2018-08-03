"""
Template helpers
These will be accessible as 'h.' in all mako templates
"""
import random
import logging

import pyramid.traversal

from calaldees.data import first
from calaldees.string_tools import substring_in
from calaldees.files.exts import get_fileext

from karakara.traversal import TraversalGlobalRootFactory

log = logging.getLogger(__name__)


video_fileext_to_mime_types = {
    'mp4': 'mp4',
    'ogv': 'ogg',
    'mpg': 'mpeg',
    '3gp': '3gp',
    '???': 'webm',
    'mov': 'quicktime',
    'mkv': 'x-matroska',
    'wmv': 'x-ms-wmv',
    'flv': 'x-flv',
}


# A container to hold buckets of inline js to be injected into page
javascript_inline = {}


# TODO: replace url methods with constant PATH
#  templates could then use h.path.external etc
#def extneral_url(file):
#    #return request.static_url('karakara:static/%s' % file)
#    return "/ext/"+file

#def static_url(file):
#    #return request.static_url('karakara:static/%s' % file)
#    return "/static/"+file

class Path(object):
    external = '/ext/'
    static = '/static/'
path = Path()


def paths_for_queue(queue_id):
    queue_context = TraversalGlobalRootFactory(None)['queue'][queue_id]
    return {
        **{
            'queue': pyramid.traversal.resource_path(queue_context),
            'player': f'/player2/index.html#queue_id={queue_context.id}',
        },
        **{
            route_name: pyramid.traversal.resource_path(queue_context[route_name])
            for route_name in (
                'queue_items',
                'track',
                'track_list',
                'search_tags',
                'search_list',
                'settings',
                'remote_control',
                'admin',
                'priority_tokens',
            )
        }
    }


def media_url(file):
    return '/files/%s' % file


def duration_str(duration):
    """
    duration in seconds to human readable string form
    """
    try:
        duration = duration.total_seconds()
    except Exception:
        pass
    return "%d min" % (duration/60)


def attachment_location(track={}, attachment_type='preview'):
    return first(attachment_location(track, attachment_type))


def attachment_locations(track={}, attachment_type='preview'):
    return [
        (attachment, media_url(attachment['location']))
        for attachment in track.get('attachments', [])
        if attachment['type'] == attachment_type
    ]


def attachment_locations_by_type(track, attachment_type):
    return [url for attachment, url in attachment_locations(track, attachment_type)]


def thumbnail_location_from_track(track, index=0):
    thumbnails = attachment_locations_by_type(track, 'image')
    if not thumbnails:
        return ''
    if index == 'random':
        index = random.randint(0, len(thumbnails)-1)
    return thumbnails[min(index, len(thumbnails)-1)]


def video_mime_type(attachment):
    return video_fileext_to_mime_types.get(get_fileext(attachment['location']),'mp4')



# Titles from tags -------------------------------------------------------------

_test_tags = {'title':['dynamite explosion','キ'], 'from':['macross'], 'macross':['dynamite'], 'category':['anime','jpop'], 'use':['opening','op1'], 'artist':['firebomber']}


def tag_hireachy(tags, tag):
    """
    >>> tag_hireachy(_test_tags, 'from')
    'macross: dynamite'
    >>> tag_hireachy(_test_tags, 'category')
    'anime, jpop'
    """
    if tag not in tags:
        return ''
    tag_value = ', '.join(tags[tag])
    subtag_value = tag_hireachy(tags, tag_value)
    if tag_value and subtag_value:
        return '{0}: {1}'.format(tag_value, subtag_value)
    return tag_value


title_tags_for_category = {
    'DEFAULT': ['from', 'use', 'title', 'length'],
    'jpop': ['artist', 'title'],
    'meme': ['title', 'from'],
}
def track_title(tags, exclude_tags=[]):
    """
    >>> import copy
    >>> track_title(_test_tags)
    'Macross: Dynamite - Opening, Op1 - Dynamite Explosion, キ'
    >>> track_title(_test_tags, exclude_tags=['from:macross'])
    'Dynamite - Opening, Op1 - Dynamite Explosion, キ'
    >>> _test_tags_artist = copy.copy(_test_tags)
    >>> _test_tags_artist['category'] = ['jpop','anime']
    >>> track_title(_test_tags_artist)
    'Firebomber - Dynamite Explosion, キ'
    """
    from_exclude = list(filter(lambda t: t.startswith('from:'), exclude_tags))
    from_include = [from_exclude.pop().split(':').pop().strip()] if from_exclude else []
    exclude_tags = [tag.split(':')[0] for tag in exclude_tags]  # setup initial exclude tags from passed args
    if substring_in(tags.get('title'), tags.get('from')):  # if 'title' is in 'from' - exclude title as it is a duplicate
        exclude_tags.append('title')
    title_tags = title_tags_for_category.get(tags.get('category', 'DEFAULT')[0], title_tags_for_category['DEFAULT'])  # get tags to use in the constuction of this category
    tags_to_use = from_include + list(filter(lambda t: t not in exclude_tags, title_tags))  # remove exclude tags from tag list
    return " - ".join(filter(None, (tag_hireachy(tags, tag) for tag in tags_to_use))).title()


def track_title_only(tags):
    """
    >>> track_title_only(_test_tags)
    'Dynamite Explosion, キ'
    """
    #title = track.get('title')
    title = ''
    for tag in ['title', 'from', 'artist']:
        title = tag_hireachy(tags, tag)  # track['tags'][tag][0]
        if title:
            break
    return title.title()
