from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from .                    import web
from ..lib.auto_format    import action_ok
from ..templates.helpers  import search_url

#-------------------------------------------------------------------------------
# Faves
#-------------------------------------------------------------------------------

@view_config(route_name='fave', request_method='GET')
@web
def fave_view(request):
    """
    view current faves
    """
    trackids = request.session['faves']
    if request.matchdict['format']=='html':
        raise HTTPFound(location=search_url(trackids=trackids,route='search_list'))
    return action_ok(
        data={'faves':trackids}
    )

@view_config(route_name='fave', request_method='POST')
@web
def fave_add(request):
    """
    Add item to faves in session
    """
    if 'fave' not in request.session:
        request.session['faves'] = []
    request.session['faves'].append(request.params['id'])
    return action_ok(message='added to faves')

@view_config(route_name='fave', request_method='DELETE')
@web
def fave_del(request):
    """
    Remove fave from session
    """
    return action_ok()
