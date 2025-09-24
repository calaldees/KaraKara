import uuid
import dataclasses


@dataclasses.dataclass
class User:
    is_admin: bool
    session_id: str

class LoginManager:
    @staticmethod
    def login(room_name: str, username: str | None, password: str, requested_session: str | None = None) -> User:
        if password==room_name:
            session_id = "admin"
        else:
            session_id = requested_session or str(uuid.uuid4())
        return User(is_admin = password==room_name, session_id=session_id)

    @staticmethod
    def from_session(session_id: str) -> User:
        return User(is_admin = session_id=="admin", session_id=session_id)
