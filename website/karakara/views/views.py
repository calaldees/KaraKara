from pyramid.view import view_config

from ..lib.auto_format    import auto_format_output


#-------------------------------------------------------------------------------
# Misc
#-------------------------------------------------------------------------------
@view_config(route_name='home')
@auto_format_output
def home(request):
    return {'status':'ok','message':'Hello World'}
