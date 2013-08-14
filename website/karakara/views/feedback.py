from pyramid.view import view_config

from . import web
from ..lib.auto_format    import action_ok, action_error
from ..lib.misc           import strip_non_base_types

from ..model                import DBSession
from ..model.model_feedback import Feedback

import logging
log = logging.getLogger(__name__)


@view_config(route_name='feedback')
@web
def feedback_view(request):
    """
    Feedback
    """
    if request.method == 'GET':
        if request.session.get('admin'):
            return action_ok(data={'feedback': [feedback.to_dict() for feedback in DBSession.query(Feedback)]})
        return action_ok()
    
    if not request.params.get('details'):
        raise action_error('Please provide feedback details', code=400)
    
    feedback = Feedback()
    for field, value in request.params.items():
        try   : setattr(feedback,field,value)
        except: pass
    feedback.environ = strip_non_base_types(request.environ)
    DBSession.add(feedback)
    
    return action_ok(message='Feedback received, thank you!')
