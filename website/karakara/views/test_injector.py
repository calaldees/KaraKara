from pyramid.view import view_config

from . import web, is_admin

from ..lib.auto_format    import action_ok, action_error

#from ..model              import DBSession
#from ..model.model_tracks import Track
#from ..model.model_queue  import QueueItem

import datetime
import random

import logging
log = logging.getLogger(__name__)


@view_config(route_name='test_injector')
@web
def test_injector(request):
    """
    """
    if not is_admin(request):
        raise action_error(message='Test injector for admin only', code=403)
    
    return action_ok()
