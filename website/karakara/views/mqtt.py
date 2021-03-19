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

    # Admin user not associated with any particular queue
    if username == "karakara" and password == "aeyGGrYJ":
        return action_ok(message="admin ok")

    if not password:
        raise action_error(message="no password specified", code=403)

    if not queue_setting_password:
        raise action_error(message="queue has no password", code=403)

    if password == queue_setting_password.value:
        return action_ok(message="queue owner ok")

    raise action_error(message="login failed", code=403)


@view_config(
    context='karakara.traversal.MQTTAclContext',
)
def acl(request):
    _ = request.translate
    clientid: str = request.params.get("clientid")
    username: str = request.params.get("username")
    topic: str = request.params.get("topic")
    access: str = request.params.get("access")

    log.info(f'checking acls for {clientid} / {username} / {topic} / {access}')

    # KaraKara is the admin user who can read/write everything
    if username == "karakara":
        return action_ok(message="admin ok")

    # Special cases for unit tests
    if topic.startswith("test/public/"):
        return action_ok(message="public test ok")
    if username == "test" and topic.startswith("test/private/"):
        return action_ok(message="private test ok")

    # Each room can write to its own topics
    if topic.startswith("karakara/room/{username}/"):
        return action_ok(message="queue owner ok")

    # Everybody can subscribe to room state broadcasts
    if topic.startswith("karakara/room/") and access == "read":
        return action_ok(message="anon read ok")

    raise action_error(message="login failed", code=403)
