import contextlib
import dataclasses
from abc import abstractmethod
import csv
from pathlib import Path
import io
import asyncio
from collections import defaultdict
import typing as t

from .settings_manager import SettingsManager
from .queue_model import Queue, QueueItem


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

    #@abstractmethod
    #def queue_names(self, newer_than_timestamp:float = 0) -> t.Sequence[str]:
    #    ...

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

    def path_csv(self, name) -> Path:
        return self.path.joinpath(f'{name}.csv')

    def for_json(self, name) -> t.Sequence[t.Mapping[str, t.Any]]:
        file_context = self.path_csv(name).open('r', encoding='utf8') if self.path_csv(name).is_file() else io.StringIO('')
        with file_context as filehandle:
            return tuple(QueueItem(**row).asdict() for row in csv.DictReader(filehandle))  # type: ignore[arg-type]  # dataclass.__post_init__ takes care of the types in `**row`

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

