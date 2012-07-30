from pyramid.view import view_config

from sqlalchemy.orm import joinedload

from . import web, etag

from ..lib.auto_format    import action_ok
from ..model              import DBSession
from ..model.model_tracks import Track
from ..model.model_queue  import QueueItem



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
                )
    track = track.get(id).to_dict('full')
    
    queue = DBSession.query(QueueItem).\
                filter(QueueItem.status=='pending').\
                filter(QueueItem.track_id==track['id']).\
                order_by(QueueItem.id)
    queue = [queue_item.to_dict('full', exclude_fields='track_id,session_owner') for queue_item in queue]
    
    return action_ok(data={
        'track' : track,
        'queued': queue,
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

