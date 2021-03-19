from pyramid.view import view_config

from . import action_ok, action_error

from ..model import DBSession
from ..model.model_queue import QueueSetting


def user(request):
    _ = request.translate
    username: str = request.params.get("username")
    password: str = request.params.get("password")

    queue_setting_password = DBSession.query(QueueSetting).filter(
        QueueSetting.queue_id == username, QueueSetting.key == 'karakara.private.password'
    ).one()

    log.info(f'trying to mqtt-auth as user {username}')

    # Not a real user, used for unit tests
    if username == "test" and password == "test":
        return action_ok()

    # Admin user not associated with any particular queue
    if username == "karakara" and password == "aeyGGrYJ":
        return action_ok()

    if password == queue_setting_password.value:
        return action_ok()
    else:
        raise action_error(code=403)


def acl(request):
    _ = request.translate
    clientid: str = request.params.get("clientid")
    username: str = request.params.get("username")
    topic: str = request.params.get("topic")
    access: str = request.params.get("access")

    log.info(f'checking acls for {clientid} / {username} / {topic} / {access}')

    # KaraKara is the admin user who can read/write everything
    if username == "karakara":
        return action_ok()

    # Special cases for unit tests
    if topic.startswith("test/public/"):
        return action_ok()
    if username == "test" and topic.startswith("test/private/"):
        return action_ok()

    # Each room can write to its own topics
    if topic.startswith("karakara/room/{username}/"):
        return action_ok()

    # Everybody can subscribe to room state broadcasts
    if topic.startswith("karakara/room/") and access == "read":
        return action_ok()

    raise action_error(code=403)
