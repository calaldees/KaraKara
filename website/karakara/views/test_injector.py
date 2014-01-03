from pyramid.view import view_config
from pyramid.request import Request


from . import web, admin_only

from ..lib.misc           import random_string
from ..lib.auto_format    import action_ok

from ..model              import DBSession
from ..model.model_tracks import Track


import random

import logging
log = logging.getLogger(__name__)


@view_config(route_name='inject_testdata')
@web
@admin_only
def inject_testdata(request):
    """
    When demoing the system to new people it was often an annoyance to manually
    add multiple tracks to show the priority token system.
    This is a nice way to quickly add test tracks.
    """
    message = ''
    if (request.params.get('cmd') == 'add_queue_item'):
        (random_track_id, ) = random.choice(DBSession.query(Track.id).all())
        random_performer_name = random.choice(('Bob','Jane','Sally','Brutus','Rasputin','Lisa','Ryu','Ken','Alec Baldwin','Ghengis Kahn','Kraken','Lucy'))
        queue_track_request = Request.blank('/queue.json', POST={
            'track_id': random_track_id,
            'performer_name': random_performer_name,
            'session_owner': random_string(),
        })
        response_json = request.invoke_subrequest(queue_track_request).json
        message = response_json['messages'].pop()
    
    return action_ok(message=message)
