from pyramid.view import view_config

from . import web, etag

from ..lib.auto_format    import action_ok
from ..model              import DBSession
from ..model.model_tracks import Track



# Fake Etag placeholder
from ..lib.misc import random_string
tracks_instance_id = None
def tracks_updated():
    global tracks_instance_id
    tracks_instance_id = random_string()
tracks_updated()
def tracks_etag(request):
    global tracks_instance_id
    return tracks_instance_id + str(request.session.peek_flash())


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
    track = DBSession.query(Track).with_polymorphic('*').get(id)
    
    #request.session['track_views'] = request.session.get('track_views',0) + 1
    #d = {'description':track.description, 'views':request.session['track_views']}
    
    return action_ok(data=track.to_dict('full'))


@view_config(route_name='track_list')
@etag(tracks_etag)
@web
def track_list(request):
    """
    Browse tracks
    """
    #track_list = []
    #for track in DBSession.query(Track).all():
    #    track_list.append(track.id)
    track_list = [track.to_dict() for track in DBSession.query(Track).all()]
    return action_ok(data={'list':track_list})


@view_config(route_name='track_list_all')
@web
def track_list_all(request):
    """
    Return a list of every track in the system (typically for printing)
    """
    return action_ok()

