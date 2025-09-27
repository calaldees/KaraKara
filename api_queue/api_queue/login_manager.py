from pathlib import Path
import json
import contextlib
import typing as t
import pydantic


T = t.TypeVar("T", bound=pydantic.BaseModel)


@contextlib.contextmanager
def load_obj(path: Path, cls: type[T]) -> t.Generator[T]:
    oldData: dict[str, t.Any] = json.loads(path.read_text()) if path.is_file() else {}
    obj = cls.model_validate(oldData)
    yield obj
    newData = obj.model_dump(mode="json")
    if oldData != newData:
        path.write_text(json.dumps(newData, indent=4))


class RoomAccounts(pydantic.BaseModel):
    admin_sessions: set[str] = set()


class User(pydantic.BaseModel):
    is_admin: bool = False


class LoginManager:
    def __init__(self, path: Path) -> None:
        self.path = path

    def login(
        self,
        room_name: str,
        session_id: str,
        password: str,
    ) -> User:
        with load_obj(self.path / f"{room_name}_accounts.json", RoomAccounts) as accounts:
            if password == room_name:
                if session_id not in accounts.admin_sessions:
                    accounts.admin_sessions.add(session_id)
                return User(is_admin=True)
            else:
                if session_id in accounts.admin_sessions:
                    accounts.admin_sessions.remove(session_id)
                return User(is_admin=False)

    def load(
        self,
        room_name: str,
        session_id: str | None,
    ) -> User:
        if session_id is None:
            return User(is_admin=False)
        with load_obj(self.path / f"{room_name}_accounts.json", RoomAccounts) as accounts:
            return User(is_admin=session_id in accounts.admin_sessions)
