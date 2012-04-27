from pyramid.view import view_config
from pyramid.response import Response

from karakara.lib.auto_format import auto_format_output

@view_config(route_name='home')
@auto_format_output
def home(request):
    return {'status':'ok','message':'Hello World'}
