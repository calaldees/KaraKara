from pyramid.view import view_config
from pyramid.response import Response

from .models import (
    DBSession,
    MyModel,
    )

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
    return {'one':one, 'project':'KaraKara'}

@view_config(route_name='helloworld')
def helloworld(request):
    return Response('Hello World')