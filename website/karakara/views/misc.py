from pyramid.view import view_config

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

