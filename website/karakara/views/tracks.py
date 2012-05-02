from pyramid.view import view_config

from ..lib.auto_format    import auto_format_output, action_ok
from ..model.models       import DBSession
from ..model.model_tracks import Track



#-------------------------------------------------------------------------------
# Track
#-------------------------------------------------------------------------------

@view_config(route_name='track')
@auto_format_output
def track_view(request):
    """
    View individual track details
    """
    id    = request.matchdict['id']
    track = DBSession.query(Track).with_polymorphic('*').get(id)
    
    request.session['track_views'] = request.session.get('track_views',0) + 1
    
    return action_ok(message='track test', data={'description':track.description, 'views':request.session['track_views']})


@view_config(route_name='track_list')
@auto_format_output
def track_list(request):
    """
    Browse tracks
    """
    track_list = []
    for track in DBSession.query(Track).all():
        track_list.append(track.id)
    return action_ok(data={'list':track_list})


@view_config(route_name='track_list_all')
@auto_format_output
def track_list_all(request):
    """
    Return a list of every track in the system (typically for printing)
    """
    return action_ok()

