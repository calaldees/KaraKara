from pyramid.view import view_config

from . import action_ok, action_error

from ..model import DBSession
from ..model.model_queue import QueueSetting

import logging
log = logging.getLogger(__name__)


@view_config(
    context='karakara.traversal.MQTTUserContext',
)
def user(request):
    _ = request.translate
    username: str = request.params.get("username")
    password: str = request.params.get("password")

    queue_setting_password = DBSession.query(QueueSetting).filter(
        QueueSetting.queue_id == username, QueueSetting.key == 'karakara.private.password'
    ).first()

    log.info(f'trying to mqtt-auth as user {username}')

    # Not a real user, used for unit tests
    if username == "test" and password == "test":
        return action_ok(message="test ok")

    if not password:
        raise action_error(message="no password specified", code=403)

    if not queue_setting_password:
        raise action_error(message="queue has no password", code=403)

    if password == queue_setting_password.value:
        return action_ok(message="queue owner ok")

    raise action_error(message="login failed", code=403)
