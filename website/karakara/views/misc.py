from pyramid.view import view_config

import re

from . import web, method_put_router, is_admin
from ..lib.auto_format import action_ok, action_error
from ..lib.misc import convert_str_with_type

import logging
log = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
# Misc
#-------------------------------------------------------------------------------
@view_config(route_name='home')
@web
def home(request):
    #request.session.flash('Hello World')
    #from ..model import DBSession
    #from ._logic import issue_priority_token
    #issue_priority_token(request, DBSession)
    return action_ok()

@view_config(route_name='admin_lock')
@web
def admin_lock(request):
    if is_admin(request):
        request.registry.settings['admin_locked'] = not request.registry.settings.get('admin_locked',False)
    return action_ok()

@view_config(route_name='admin_toggle')
@web
def admin_toggle(request):
    if request.registry.settings.get('admin_locked'):
        raise action_error(message='additional admin users have been prohibited', code=403)
    request.session['admin'] = not request.session.get('admin',False)
    return action_ok()

@view_config(route_name='remote')
@web
def remote(request):
    cmd = request.params.get('cmd')
    if is_admin(request) and cmd:
        log.debug("sending {0}".format(cmd))
        request.registry['socket_manager'].recv(cmd.encode('utf-8'))
    return action_ok()

@view_config(route_name='settings')
@web
def settings(request):
    """
    Surface settings as an API.
    This allows clients to qurey server settup rather than having to hard code bits into the clients
    """
    
    if method_put_router(None, request):
        # with PUT requests, update settings
        #  only changing in production is bit over zelious #request.registry.settings.get('karakara.server.mode')!='production'
        if request.registry.settings.get('karakara.server.mode')!='test' and not is_admin(request):
            raise action_error(message='Settings unavalable for non admin users', code=403)
        
        for key, value in request.params.items():
            request.registry.settings[key] = convert_str_with_type(value)
    
    setting_regex = re.compile(request.registry.settings.get('api.settings.regex','TODOmatch_nothing_regex'))
    return action_ok(
        data={
            'settings': {
                setting_key:request.registry.settings.get(setting_key)
                for setting_key in
                [setting_key for setting_key in request.registry.settings.keys() if setting_regex.match(setting_key)]
            }
        }
    )
