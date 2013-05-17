from pyramid.view import view_config

import re

from . import web, method_put_router
from ..lib.auto_format import action_ok
from ..lib.misc import convert_str_with_type


#-------------------------------------------------------------------------------
# Misc
#-------------------------------------------------------------------------------
@view_config(route_name='home')
@web
def home(request):
    #request.session.flash('Hello World')
    from ..model import DBSession
    from ._logic import issue_priority_token
    issue_priority_token(request, DBSession)
    return action_ok()

@view_config(route_name='admin_toggle')
@web
def admin_toggle(request):
    request.session['admin'] = not request.session.get('admin',False)
    return action_ok()

@view_config(route_name='settings')
@web
def settings(request):
    """
    Surface settings as an API.
    This allows clients to qurey server settup rather than having to hard code bits into the clients
    """
    # with PUT requests, update settings
    if request.registry.settings.get('karakara.server.mode')!='production' and method_put_router(None, request):
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
