import json

from pyramid.view import view_config

from . import web, action_ok, action_error, admin_only, etag_decorator, generate_cache_key

from ..model import DBSession
from ..model.model_tracks import Track


import logging
log = logging.getLogger(__name__)


@view_config(route_name='track_import', request_method='GET')
@web
def existing_track_ids(request):
    return action_ok(data={
        'track_ids': {t.id for t in DBSession.query(Track.id)}
    })


@view_config(route_name='track_import', request_method='POST')
@web
def track_import_post(request):
    #track_id = request.params.get('track_id')
    try:
        data = request.json
    except json.JSONDecodeError:
        raise action_error('required json track data to import', code=400)
    #import pdb ; pdb.set_trace()
    return action_ok()


@view_config(route_name='track_import', request_method='DELETE')
@web
def track_delete(request):
    return action_ok()
