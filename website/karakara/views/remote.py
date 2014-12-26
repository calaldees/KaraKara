from pyramid.view import view_config

from . import web, action_ok, admin_only

import logging
log = logging.getLogger(__name__)


def send_socket_message(request, message):
    request.registry['socket_manager'].recv(message.encode('utf-8'))  # TODO: ?um? new_line needed?


@view_config(route_name='remote')
@web
@admin_only
def remote(request):
    cmd = request.params.get('cmd')
    if cmd:
        log.debug("remote command - {0}".format(cmd))
        send_socket_message(request, cmd)
    return action_ok()
