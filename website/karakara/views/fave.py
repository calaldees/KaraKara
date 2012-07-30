from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from .                    import web, method_delete_router
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
    
    not really needed as faves are also part of the identity dict
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
    if 'faves' not in request.session:
        request.session['faves'] = []
    request.session['faves'].append(request.params['id'])
    return action_ok(message='added to faves')

@view_config(route_name='fave', custom_predicates=(method_delete_router, lambda info,request: request.params.get('id'))) #request_method='DELETE'
@web
def fave_del(request):
    """
    Remove fave from session
    """
    request.session['faves'].remove(request.params['id'])
    return action_ok(message='removed from faves')
