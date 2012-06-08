from pyramid.view import view_config

from . import base
from ..lib.auto_format import auto_format_output, action_ok


#-------------------------------------------------------------------------------
# Misc
#-------------------------------------------------------------------------------
@view_config(route_name='home')
@base
@auto_format_output
def home(request):
    #request.session.flash('Hello World')
    return action_ok()

