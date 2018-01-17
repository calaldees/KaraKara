import random

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.traversal import resource_path

from externals.lib.misc import subdict, first

from . import web, action_ok, action_error, etag_decorator, cache, cache_none, generate_cache_key, admin_only, cache_manager
#from ._logic import queue_item_for_track

from ..model import DBSession
from ..model.actions import get_track_dict_full
from ..model.model_tracks import Track

from ..templates.helpers import track_title #, track_url

import logging
log = logging.getLogger(__name__)


#-------------------------------------------------------------------------------
# Cache Management
#-------------------------------------------------------------------------------
#TRACK_CACHE_KEY = 'track'

#track_version = {}
#def track_key(id):
#    return "{0}:{1}".format(TRACK_CACHE_KEY, id)
#def invalidate_track(id):
#    cache.delete(track_key(id))
#    global track_version
#    if id not in track_version:
#        track_version[id] = random.randint(0, 65535)  # TODO: this is nieve that we don't have overlapping id's
#    track_version[id] += 1
#def get_trackid_from_request(request):
#    # TODO: Pollyfill for url_dispatch and traversal. Can probably be reduced to context.id in the future
#    return (request.matchdict.get('id') if request.matchdict else None) or request.context.id
#def generate_cache_key_track(request):
#    global track_version
#    return '-'.join([
#        generate_cache_key(request),
#        str(track_version.get(get_trackid_from_request(request), -1)),
#        str(request.registry.settings.get('karakara.system.user.readonly')),
#    ])

def acquire_cache_bucket_func(request):
    return cache_manager.get(f'queue-{request.context.queue_id}-track-{request.context.id}')

#-------------------------------------------------------------------------------
# Track
#-------------------------------------------------------------------------------

@view_config(
    context='karakara.traversal.TrackContext',
    acquire_cache_bucket_func=acquire_cache_bucket_func,
)
def track_view(request):
    """
    View individual track details

    This method has two levels of cache:
     - track_dict cache - cache the track data (should not change)
     - track_dict + queue_dict - every time this track is modifyed in the queue it will invalidate the cache

    The track dicts that are fetched from the DB are cached with infinate expiray
    time as they will not change once the system is running

    It might be wise to add an cache_clear to the import_tracks operation
    (currently this wont be needed as the basic implementation is python_dict,
     which is invalidatated on shutdown,
     but if we were going to use memcache or redis then this is nessisary)
    """
    id = request.context.id
    if not id:
        raise HTTPNotFound()

    # Search, find and redirect for shortened track id's
    # This is kind of a hack to allow id's shorter than 64 characters in tests
    if len(id) != 64:
        full_id = first(DBSession.query(Track.id).filter(Track.id.like('{0}%'.format(id))).first())
        if full_id and len(id) != len(full_id):
            raise HTTPFound(location=resource_path(request.context.queue_context['track'][full_id]))

    def get_track_dict(id):
        try:
            log.debug(f'cache gen - track_dict for {id}')
            track_dict = get_track_dict_full(id)
            track_dict['title'] = track_title(track_dict['tags'])
            return track_dict
        except (KeyError, TypeError):
            return cache_none

    def get_track_and_queued_dict(id):
        track = cache_manager.get(f'''track_dict-{id}-{request.registry.settings['karakara.tracks.version']}''').get_or_create(lambda: get_track_dict(id))
        if not track:
            return cache_none
        log.debug(f'cache gen - track_queue_dict for {id}')
        def queue_item_list_to_dict(queue_items):
            return [queue_item.to_dict('full', exclude_fields='track_id,session_owner') for queue_item in queue_items]
        queue_item_for_track_dict = subdict(
            request.queue.for_track(track['id']),
            {'played', 'pending'}
        )
        track['queue'] = {k: queue_item_list_to_dict(v) for k, v in queue_item_for_track_dict.items()}
        return track

    # TODO: Put some thought into the idea that a malicious cock could deliberately
    #       perform repeated calls knowing a cache key could well be created and
    #       take the system down with an 'out of memory'. Then again, if they want to
    #       attack this system with brains there is very little we can do to prevent
    #       every attack vector.
    track = request.cache_bucket.get_or_create(lambda: get_track_and_queued_dict(id))
    if not track:
        raise action_error(message='track {0} not found'.format(id), code=404)

    request.log_event(track_id=id, title=track['title'])

    return action_ok(data={'track': track})

