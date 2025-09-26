from pathlib import Path

from api_queue.login_manager import LoginManager


def test_login_manager(tmp_path: Path):
    lm = LoginManager(tmp_path)

    # a given session is user by default
    user = lm.load("test_room", "my_session_id")
    assert user.is_admin is False

    # login with wrong password -> still user
    user = lm.login("test_room", "my_session_id", "password123")
    assert user.is_admin is False

    # login with correct password -> become admin
    user = lm.login("test_room", "my_session_id", "test_room")
    assert user.is_admin is True

    # further request from the same session are still admin
    user = lm.load("test_room", "my_session_id")
    assert user.is_admin is True

    # login with wrong password -> downgrades to user
    user = lm.login("test_room", "my_session_id", "")
    assert user.is_admin is False

    # further request from the same session are no longer admin
    user = lm.load("test_room", "my_session_id")
    assert user.is_admin is False
