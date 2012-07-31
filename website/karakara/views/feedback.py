from pyramid.view import view_config

from . import web
from ..lib.auto_format    import action_ok

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
    
    feedback = Feedback()
    for field, value in request.params.items():
        try   : setattr(feedback,field,value)
        except: pass
    feedback.environ = request.environ
    DBSession.add(feedback)
    
    return action_ok(message='feedback recived')
