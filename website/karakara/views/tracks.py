from pyramid.view import view_config

from sqlalchemy.orm import joinedload

from . import web, etag, cache, cache_none
from ._logic import queue_item_for_track

from ..lib.auto_format    import action_ok
from ..model              import DBSession
from ..model.model_tracks import Track
from ..model.model_queue  import QueueItem

import datetime


# Fake Etag placeholder
from ..lib.misc import random_string
tracks_instance_id = None
def tracks_updated():
    global tracks_instance_id
    tracks_instance_id = random_string()
tracks_updated()
def tracks_etag(request):
    global tracks_instance_id
    return tracks_instance_id + str(request.session.get('admin',False)) + str(request.session.peek_flash())


#-------------------------------------------------------------------------------
# Track
#-------------------------------------------------------------------------------

@view_config(route_name='track')
@web
def track_view(request):
    """
    View individual track details
    The track dicts that are fetched from the DB are cached with infinate expiray
    time as they will not change once the system is running
    
    It might be wise to add an cache_clear to the import_tracks operation
    (currently this wont be needed as the basic implementation is python_dict,
     which is invalidatated on shutdown,
     but if we were going to use memcache or redis then this is nessisary)
    """
    
    def get_track_dict(id):
        try:
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
    
    id = request.matchdict['id']
    track = cache.get_or_create("track:{0}".format(id), lambda: get_track_dict(id))
    if not track:
        raise action_error(message='track {0} not found'.format(id))
    
    def queue_item_list_to_dict(queue_items):
        return [queue_item.to_dict('full', exclude_fields='track_id,session_owner') for queue_item in queue_items]
    track['queue'] = queue_item_for_track(request, DBSession, track['id'])
    track['queue']['played' ] = queue_item_list_to_dict(track['queue']['played'] )
    track['queue']['pending'] = queue_item_list_to_dict(track['queue']['pending'])
    
    return action_ok(data={
        'track' : track
    })


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
def track_list_all(request):
    """
    Return a list of every track in the system (typically for printing)
    """
    tracks = DBSession.query(Track).\
                options(\
                    joinedload(Track.tags),\
                    joinedload('tags.parent')\
                )
    return action_ok(data={'list':[track.to_dict(include_fields='tags') for track in tracks]})

