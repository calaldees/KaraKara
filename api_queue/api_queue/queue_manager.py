import contextlib
import dataclasses
import datetime
from typing import Iterator, Optional
import csv
from pathlib import Path
import io
import asyncio
from collections import defaultdict

import ujson as json
from pytimeparse.timeparse import timeparse

from .queue_model import Queue, QueueItem


DEFAULT_QUEUE_SETTINGS = {
    "track_space": 15.0,
    "hidden_tags": ["red:duplicate"],
    "forced_tags": [],
    "title": "KaraKara",
    "theme": "metalghosts",
    "preview_volume": 0.2,
    "validation_event_start_datetime": None,
    "validation_event_end_datetime": None,
    "validation_duplicate_performer_timedelta": None,
    "validation_duplicate_track_timedelta": None,
    "validation_performer_names": [],
    "validation": ['default'],
}
def _parse_isodatetime(isoformatString):
    return datetime.datetime.fromisoformat(isoformatString) if isoformatString else None
def _parse_timedelta(durationString):
    return datetime.timedelta(seconds=timeparse(durationString)) if durationString else None
QUEUE_SETTING_TYPES = {
    "track_space": lambda x: datetime.timedelta(seconds=x),
    "validation_event_start_datetime": _parse_isodatetime,
    "validation_event_end_datetime": _parse_isodatetime,
    "validation_duplicate_performer_timedelta": _parse_timedelta,
    "validation_duplicate_track_timedelta": _parse_timedelta,
}

class SettingsManager():
    def __init__(self, path: Path = Path('.')):
        path = path if isinstance(path, Path) else Path(path)
        path.mkdir(parents=True, exist_ok=True)  # is this safe?
        assert path.is_dir()
        self.path = path

    def get_json(self, name) -> dict:
        path = self.path.joinpath(f'{name}_settings.json')
        if not path.is_file():
            return DEFAULT_QUEUE_SETTINGS
        with path.open('r') as filehandle:
            return {**DEFAULT_QUEUE_SETTINGS, **json.load(filehandle)}

    def set_json(self, name, settings) -> None:
        old_settings = self.get_json(name)
        path = self.path.joinpath(f'{name}_settings.json')
        with path.open('w') as filehandle:
            json.dump({**old_settings, **settings}, filehandle)

    def get(self, name) -> dict:
        return {
            k: QUEUE_SETTING_TYPES.get(k, lambda x: x)(v)
            for k, v in self.get_json(name).items()
        }


@dataclasses.dataclass
class User:
    is_admin: bool

class LoginManager:
    @staticmethod
    def login(session_id: str, queue_id: str, username: Optional[str], password: str) -> User:
        return User(is_admin = password==queue_id)

    @staticmethod
    def from_session(session_id: str) -> User:
        return User(is_admin = session_id=="admin")


class QueueManager():
    def __init__(self, *args, settings: SettingsManager=None, **kwargs):
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

