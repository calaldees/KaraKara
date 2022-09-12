import contextlib
import dataclasses
import datetime
import random
import numbers
from functools import reduce
from itertools import pairwise
from typing import Iterator
import csv
from pathlib import Path
import io
import asyncio
from collections import defaultdict
from functools import cache

try:
    import ujson as json
except ImportError:
    import json


DEFAULT_QUEUE_SETTINGS = {
    "track_space": 15.0,
    "hidden_tags": ["red:duplicate"],
    "forced_tags": [],
    "title": "KaraKara",
    "theme": "metalghosts",
    "preview_volume": 0.2,
    "event_end": None,
}
QUEUE_SETTING_TYPES = {
    "track_space": lambda x: datetime.timedelta(seconds=x),
}

class SettingsManager():
    def __init__(self, path: Path = Path('.')):
        path = path if isinstance(path, Path) else Path(path)
        path.mkdir(parents=True, exist_ok=True)  # is this safe?
        assert path.is_dir()
        self.path = path

    @cache
    def get_json(self, name) -> dict:
        path = self.path.joinpath(f'{name}_settings.json')
        if not path.is_file():
            return DEFAULT_QUEUE_SETTINGS
        with path.open('r') as filehandle:
            return {**DEFAULT_QUEUE_SETTINGS, **json.load(filehandle)}
    @cache
    def get(self, name) -> dict:
        return {
            k: QUEUE_SETTING_TYPES.get(k, lambda x: x)(v)
            for k, v in self.get_json(name).items()
        }



class QueueManager():
    def __init__(self, *args, settings: SettingsManager=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings
        assert isinstance(settings, SettingsManager)

    @contextlib.contextmanager
    def _queue_modify_context(self, name, filehandle):
        queue = Queue([QueueItem(**row) for row in csv.DictReader(filehandle)], **self.settings.get(name))
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



# dataclasses are ment to be this cool hip new happening pattern in python
# have I missed the point here? this feels like verbose rubbish for such a simple class
@dataclasses.dataclass
class QueueItem():
    track_id: str
    track_duration: datetime.timedelta
    session_id: str
    performer_name: str
    start_time: datetime.datetime = None
    id: float = dataclasses.field(default_factory=random.random)

    def __post_init__(self):
        """
        >>> QueueItem('Track1', 60.25, 'Session1', 'test_name', 123456789.123456789, 0.123456789)
        QueueItem(track_id='Track1', track_duration=datetime.timedelta(seconds=60, microseconds=250000), session_id='Session1', performer_name='test_name', start_time=datetime.datetime(1973, 11, 29, 21, 33, 9, 123457), id=0.123456789)
        >>> QueueItem('Track1', '60.25', 'Session1', 'test_name', '123456789.123456789', '0.123456789')
        QueueItem(track_id='Track1', track_duration=datetime.timedelta(seconds=60, microseconds=250000), session_id='Session1', performer_name='test_name', start_time=datetime.datetime(1973, 11, 29, 21, 33, 9, 123457), id=0.123456789)
        >>> QueueItem('', '', '', '', '', 0.123456789)
        QueueItem(track_id='', track_duration=datetime.timedelta(0), session_id='', performer_name='', start_time=None, id=0.123456789)
        """
        if not self.track_duration:
            self.track_duration = 0.0
        if isinstance(self.track_duration, str):
            self.track_duration = float(self.track_duration)
        self.track_duration = datetime.timedelta(seconds=self.track_duration) if isinstance(self.track_duration, numbers.Number) else self.track_duration
        if not self.start_time:
            self.start_time = None
        if isinstance(self.start_time, str):
            self.start_time = float(self.start_time)
        self.start_time = datetime.datetime.fromtimestamp(self.start_time) if isinstance(self.start_time, numbers.Number) else self.start_time
        self.id = float(self.id)
    def asdict(self):
        return dataclasses.asdict(self, dict_factory=self.dict_factory)
    @staticmethod
    def dict_factory(key_values):
        """
        >>> i = QueueItem('Track1', 60.25, 'Session1', 'test_name', 123456789.123456789, 0.123456789)
        >>> i.asdict()
        {'track_id': 'Track1', 'track_duration': 60.25, 'session_id': 'Session1', 'performer_name': 'test_name', 'start_time': 123456789.123457, 'id': 0.123456789}
        """
        def _parse(dd):
            k, v = dd
            if isinstance(v, datetime.timedelta):
                v = v.total_seconds()
            elif isinstance(v, datetime.datetime):
                v = v.timestamp()
            return (k, v)
        return dict(map(_parse, key_values))

    @property
    def end_time(self) -> datetime.datetime:
        if self.start_time:
            return self.start_time + self.track_duration


class Queue():
    def __init__(self, items: list[QueueItem], track_space: datetime.timedelta):
        self.items = items
        self.track_space = track_space
        self.modified = False
        self._now = None
    @property
    def now(self) -> datetime.datetime:
        return self._now or datetime.datetime.now()
    @property
    def past(self) -> Iterator[QueueItem]:
        now = self.now
        return (i for i in self.items if i.start_time and i.end_time < now)
    @property
    def future(self) -> Iterator[QueueItem]:
        now = self.now
        return (i for i in self.items if not i.start_time or i.start_time >= now)
    @property
    def current(self) -> QueueItem:
        return self.playing or next(self.future, None)
    @property
    def current_future(self) -> Iterator[QueueItem]:
        # fugly mess - you can do this in less lines
        current = self.current
        future = list(self.future)
        if future and future[0] != current:
            future.insert(0, current)
        return future
    @property
    def last(self) -> QueueItem:
        return self.items[-1] if self.items else None
    @property
    def playing(self) -> QueueItem:
        now = self.now
        return next((i for i in self.items if i.start_time and i.start_time <= now and i.end_time > now), None)
    @property
    def is_playing(self) -> bool:
        return self.current and self.current.start_time
    @property
    def end_time(self) -> datetime.datetime:
        if self.last.end_time:
            return self.last.end_time
        def track_duration_reducer(end_time, i):
            end_time += i.track_duration + self.track_space
            return end_time
        return reduce(track_duration_reducer, self.future, self.now)
    def play(self) -> None:
        self.current.start_time = self.now
        self._recalculate_start_times()
    def stop(self) -> None:
        self.current.start_time = None
        self._recalculate_start_times()
    def add(self, queue_item: QueueItem) -> None:
        self.items.append(queue_item)
        self._recalculate_start_times()
    def move(self, id1: float, id2: float) -> None:
        assert {id1, id2} < {i.id for i in self.current_future}|{1,}, 'move track_ids are not in future track list'
        index1, queue_item = self.get(id1)
        del self.items[index1]
        index2, _ = self.get(id2) if id2<1 else (len(self.items), None)  # id's are always between 0 and 1. `1` is a special sentinel value for end of list
        queue_item.start_time = None
        self.items.insert(index2, queue_item)
        self._recalculate_start_times()
    def get(self, id: float) -> tuple[int, QueueItem]:
        return next(((index, queue_item) for index, queue_item in enumerate(self.items) if queue_item.id==id), (None, None))
    def delete(self, id: float) -> None:
        now = self.now
        self.items[:] = [i for i in self.items if (i.start_time and i.start_time < now) or i.id != id]
        self._recalculate_start_times()
    def _recalculate_start_times(self) -> None:
        for i_prev, i_next in pairwise(self.current_future):
            i_next.start_time = i_prev.end_time + self.track_space if i_prev and i_prev.start_time else None
        self.modified = True
