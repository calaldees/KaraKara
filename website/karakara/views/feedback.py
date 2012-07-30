from pyramid.view import view_config

from . import web
from ..lib.auto_format    import action_ok

#from ..model.model_feedback import Feedback

import logging
log = logging.getLogger(__name__)


@view_config(route_name='feedback', request_method='GET')
@web
def feedback_view(request):
    """
    View feedback
    """
    return action_ok()
    
@view_config(route_name='feedback', request_method='POST')
@web
def feedback_add(request):
    """
    Add feedback
    """
    return action_ok(message='feedback recived')