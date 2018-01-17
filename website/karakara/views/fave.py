from decorator import decorator

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from . import web, method_delete_router, action_ok, action_error, request_from_args
#from ..templates.helpers import search_url


# Utils ------------------------------------------------------------------------

@decorator
def faves_enabled(target, *args, **kwargs):
    """
    """
    request = request_from_args(args)
    if not request.registry.settings.get('karakara.faves.enabled'):
        raise action_error(message='faves disabled', code=400)
    return target(*args, **kwargs)


#-------------------------------------------------------------------------------
# Faves
#-------------------------------------------------------------------------------

@view_config(route_name='fave', request_method='GET')
@web
@faves_enabled
def fave_view(request):
    """
    view current faves

    not really needed as faves are also part of the identity dict
    """
    trackids = request.session['faves']

    if request.matchdict['format'] == 'html':
        #raise HTTPFound(location=search_url(trackids=trackids, route='search_list'))
        raise NotImplementedError()

    return action_ok(
        data={'faves': trackids}
    )


@view_config(route_name='fave', request_method='POST')
@web
@faves_enabled
def fave_add(request):
    """
    Add item to faves in session
    """
    if 'faves' not in request.session:
        request.session['faves'] = []
    request.session['faves'].append(request.params['id'])
    request.session.changed()
    return action_ok(message='added to faves')


@view_config(route_name='fave', custom_predicates=(method_delete_router, lambda info, request: request.params.get('id')))  # request_method='DELETE'
@web
@faves_enabled
def fave_del(request):
    """
    Remove fave from session
    """
    request.session['faves'].remove(request.params['id'])
    request.session.changed()
    return action_ok(message='removed from faves')
