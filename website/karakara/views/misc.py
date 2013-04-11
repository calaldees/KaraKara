from pyramid.view import view_config

import re

from . import web
from ..lib.auto_format import action_ok


#-------------------------------------------------------------------------------
# Misc
#-------------------------------------------------------------------------------
@view_config(route_name='home')
@web
def home(request):
    #request.session.flash('Hello World')
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
