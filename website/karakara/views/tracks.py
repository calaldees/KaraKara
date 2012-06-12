from pyramid.view import view_config

from . import web

from ..lib.auto_format    import action_ok
from ..model              import DBSession
from ..model.model_tracks import Track



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
    
    d = track.to_dict('full')
    
    return action_ok(data=d)


@view_config(route_name='track_list')
@web
def track_list(request):
    """
    Browse tracks
    """
    track_list = []
    for track in DBSession.query(Track).all():
        track_list.append(track.id)
    return action_ok(data={'list':track_list})


@view_config(route_name='track_list_all')
@web
def track_list_all(request):
    """
    Return a list of every track in the system (typically for printing)
    """
    return action_ok()

