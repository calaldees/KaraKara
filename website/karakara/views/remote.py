from pyramid.view import view_config

from . import web, action_ok, admin_only

import logging
log = logging.getLogger(__name__)


@view_config(route_name='remote')
@web
@admin_only
def remote(request):
    cmd = request.params.get('cmd')
    if cmd:
        log.debug("remote command - {0}".format(cmd))
        send_socket_message(request, cmd)
    return action_ok()
