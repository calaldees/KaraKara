import random

from pyramid.view import view_config

from sqlalchemy.orm import joinedload

from . import web, action_ok, action_error, etag_decorator, cache, cache_none, generate_cache_key, admin_only
from ._logic import queue_item_for_track
from .search import restrict_search

from ..model              import DBSession
from ..model.model_tracks import Track
#from ..model.model_queue  import QueueItem

import logging
log = logging.getLogger(__name__)


#-------------------------------------------------------------------------------
# Cache Management
#-------------------------------------------------------------------------------
TRACK_CACHE_KEY = 'track'

track_version = {}
def track_key(id):
    return "{0}:{1}".format(TRACK_CACHE_KEY, id)
def invalidate_track(id):
    cache.delete(track_key(id))
    global track_version
    if id not in track_version:
        track_version[id] = random.randint(0,65535)
    track_version[id] += 1
def generate_cache_key_track(request):
    global track_version
    return '-'.join([
        generate_cache_key(request),
        str(track_version.get(request.matchdict['id'],-1)),
        str(request.registry.settings.get('karakara.system.user.readonly')),
    ])

#-------------------------------------------------------------------------------
# Track
#-------------------------------------------------------------------------------

@view_config(route_name='track')
@etag_decorator(generate_cache_key_track)
@web
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
    id = request.matchdict['id']
    
    def get_track_dict(id):
        try:
            log.debug('cache gen - track_dict for {0}'.format(id))
            return DBSession.query(Track) \
                    .options( \
                        joinedload(Track.tags), \
                        joinedload(Track.attachments), \
                        joinedload('tags.parent'), \
                        joinedload('lyrics'), \
                    ) \
                    .get(id).to_dict('full')
        except AttributeError:
            return cache_none
    
    def get_track_and_queued_dict(id):
        track = cache.get_or_create("track_dict:{0}".format(id), lambda: get_track_dict(id))
        if not track:
            return cache_none
        log.debug('cache gen - track_queue_dict for {0}'.format(id))
        def queue_item_list_to_dict(queue_items):
            return [queue_item.to_dict('full', exclude_fields='track_id,session_owner') for queue_item in queue_items]
        track['queue'] = queue_item_for_track(request, DBSession, track['id'])
        track['queue']['played' ] = queue_item_list_to_dict(track['queue']['played'] )
        track['queue']['pending'] = queue_item_list_to_dict(track['queue']['pending'])
        return track
    
    # TODO: Put some thought into the idea that a malicious cock could deliberately
    #       perform repeated calls knowing a cache key could will be created and
    #       take the system down with an 'out of memory'. Then again, if they want to
    #       attack this system with brains there is very little we can do.
    track = cache.get_or_create(track_key(id), lambda: get_track_and_queued_dict(id))
    if not track:
        raise action_error(message='track {0} not found'.format(id), code=404)
    
    return action_ok(data={'track' : track})


#@view_config(route_name='track_list')
#@etag(tracks_etag)
#@web
#def track_list(request):
#    """
#    Browse tracks
#    """
#    #track_list = []
#    #for track in DBSession.query(Track).all():
#    #    track_list.append(track.id)
#    return action_ok(data={'list':[track.to_dict() for track in DBSession.query(Track).all()]})


@view_config(route_name='track_list')
@web
@admin_only
def track_list_all(request):
    """
    Return a list of every track in the system (typically for printing)
    """
    tracks = DBSession.query(Track).\
                options(\
                    joinedload(Track.tags),\
                    joinedload('tags.parent')\
                )
    tracks = restrict_search(request, tracks)
    return action_ok(data={'list':[track.to_dict(include_fields='tags') for track in tracks]})

