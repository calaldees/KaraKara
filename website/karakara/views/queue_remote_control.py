from pyramid.view import view_config

from . import web, action_ok, admin_only

import logging
log = logging.getLogger(__name__)


@view_config(
    context='karakara.traversal.RemoteControlContext',
)
@admin_only
def remote(request):
    cmd = request.params.get('cmd')
    if cmd:
        request.log_event(command=cmd)
        request.send_websocket_message('commands', cmd)
    return action_ok()
