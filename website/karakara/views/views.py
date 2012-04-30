from pyramid.view import view_config

from ..lib.auto_format    import auto_format_output
from ..model.models       import DBSession
from ..model.model_tracks import Track

@view_config(route_name='home')
@auto_format_output
def home(request):
    return {'status':'ok','message':'Hello World'}

@view_config(route_name='track')
@auto_format_output
def track(request):
    track = DBSession.query(Track).with_polymorphic('*').get(request.matchdict['id'])
    return {'status':'ok','message':track.description}
