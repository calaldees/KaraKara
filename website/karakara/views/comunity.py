from pyramid.view import view_config

from . import web, action_ok, action_error


import logging
log = logging.getLogger(__name__)


@view_config(route_name='comunity_list')
@web
def list_view(request):
    request.registry.settings['static.media']
    return action_ok()
