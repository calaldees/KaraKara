from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound


from . import web, action_ok, action_error, admin_only


import logging
log = logging.getLogger(__name__)


@view_config(
    context='karakara.traversal.TraversalGlobalRootFactory'
)
def home(request):
    # Short term hack. Do not allow normal root page in commuity mode - redirect to comunity
    # Need to implement a proper pyramid authorize system when in comunity mode
    if request.registry.settings.get('karakara.server.mode') == 'comunity':
        raise HTTPFound(location='/comunity')
    return action_ok()


#@view_config(route_name='stats')
#@web
#def stats(request):
#    return action_ok()
