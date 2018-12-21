from pyramid.view import view_config

from . import action_ok, action_error

from ..model import DBSession
from ..model.model_queue import QueueSetting


@view_config(
    context='karakara.traversal.QueueAdminContext',
)
def admin(request):
    _ = request.translate
    queue_setting_password = DBSession.query(QueueSetting).filter(QueueSetting.queue_id == request.context.queue_id, QueueSetting.key == 'karakara.private.password').one()
    if not queue_setting_password:
        raise action_error(message=_('api.queue.admin.prohibited'), code=403)
    if not request.params.get('password'):
        request.session['admin'] = False
        return action_ok(message=_('api.queue.admin.disabled'))
    elif request.params.get('password') == queue_setting_password.value:
        request.session['admin'] = True
        return action_ok(message=_('api.queue.admin.enabled'))
    else:
        raise action_error(message=_('api.queue.admin.authentication_failed'), code=403)
