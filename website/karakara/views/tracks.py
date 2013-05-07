from pyramid.view import view_config

from sqlalchemy.orm import joinedload

from . import web, etag
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
    """
    id    = request.matchdict['id']
    track = DBSession.query(Track).\
                options(\
                    joinedload(Track.tags),\
                    joinedload(Track.attachments),\
                    joinedload('tags.parent'),\
                    joinedload('lyrics')
                )
    track = track.get(id)
    if not track:
        raise action_error(message='track {0} not found'.format(id))
    track = track.to_dict('full')

    queued, queue_duplicate_status = queue_item_for_track(request, DBSession, track['id'])    
    track['queue'] = {
        'queued': [queue_item.to_dict('full', exclude_fields='track_id,session_owner') for queue_item in queued],
        'status': queue_duplicate_status,
    }
    
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

