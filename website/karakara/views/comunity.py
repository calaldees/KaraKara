from pyramid.view import view_config

import os

from . import web, action_ok, action_error


import logging
log = logging.getLogger(__name__)


@view_config(route_name='comunity_list')
@web
def list_view(request):
    path = request.registry.settings['static.media']
    return action_ok(data={
        'folders': [folder for folder in os.listdir(path) if os.path.isdir(os.path.join(path,folder))],
    })
