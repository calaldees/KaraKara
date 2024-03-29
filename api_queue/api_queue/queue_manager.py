import contextlib
import dataclasses

from typing import Iterator, Optional
import csv
from pathlib import Path
import io
import asyncio
from collections import defaultdict
import uuid

from .settings_manager import SettingsManager
from .queue_model import Queue, QueueItem



@dataclasses.dataclass
class User:
    is_admin: bool
    session_id: str

class LoginManager:
    @staticmethod
    def login(room_name: str, username: Optional[str], password: str, requested_session: Optional[str] = None) -> User:
        if password==room_name:
            session_id = "admin"
        else:
            session_id = requested_session or str(uuid.uuid4())
        return User(is_admin = password==room_name, session_id=session_id)

    @staticmethod
    def from_session(session_id: str) -> User:
        return User(is_admin = session_id=="admin", session_id=session_id)


class QueueManager():
    def __init__(self, *args, settings: SettingsManager, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings
        assert isinstance(settings, SettingsManager)

    @contextlib.contextmanager
    def _queue_modify_context(self, name, filehandle):
        queue = Queue([QueueItem(**row) for row in csv.DictReader(filehandle)], self.settings.get(name))
        yield queue
        if queue.modified:
            filehandle.seek(0)
            filehandle.truncate(0)
            fields = tuple(field.name for field in dataclasses.fields(QueueItem))
            writer = csv.DictWriter(filehandle, fields)
            writer.writeheader()
            for i in queue.items:
                writer.writerow(i.asdict())

class QueryManagerAsyncLockMixin():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue_async_locks = defaultdict(asyncio.Lock)
    @contextlib.asynccontextmanager
    async def lock_resource(self, name):
        async with self.queue_async_locks[name]:
            yield

class QueueManagerCSV(QueueManager):
    def __init__(self, path: Path = Path('.'), **kwargs):
        super().__init__(**kwargs)
        path = path if isinstance(path, Path) else Path(path)
        assert path.is_dir()
        self.path = path

    def path_csv(self, name):
        return self.path.joinpath(f'{name}.csv')

    def for_json(self, name):
        file_context = self.path_csv(name).open('r', encoding='utf8') if self.path_csv(name).is_file() else io.StringIO('')
        with file_context as filehandle:
            return tuple(QueueItem(**row).asdict() for row in csv.DictReader(filehandle))

    @contextlib.contextmanager
    def queue_modify_context(self, name):
        path_csv = self.path_csv(name)
        path_csv.touch()
        with path_csv.open('r+', encoding='utf8') as filehandle:
            with self._queue_modify_context(name, filehandle) as queue:
                yield queue

class QueueManagerCSVAsync(QueueManagerCSV, QueryManagerAsyncLockMixin):
    @contextlib.asynccontextmanager
    async def async_queue_modify_context(self, name):
        async with self.lock_resource(name):
            with self.queue_modify_context(name) as queue:
                yield queue

class QueueManagerStringIO(QueueManager):
    @contextlib.contextmanager
    def queue_modify_context(self, name):
        filehandle = io.StringIO()
        with self._queue_modify_context(name, filehandle) as queue:
            yield queue
        print('StringIO')
        print(filehandle.getvalue())

