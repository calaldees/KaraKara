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


class QueueManager():
    def __init__(self, path: Path = Path('.')):
        assert path.is_dir()
        self.path = path
        self.queue_settings = {
            'test': {
                'track_space': datetime.timedelta(seconds=15),
            }
        }
    @contextlib.asynccontextmanager
    def async_queue_modify_context(self, name):
        # open
        yield None
        # save
        # push to mqtt?
    @contextlib.contextmanager
    def queue_modify_context(self, name):
        path_csv = self.path.joinpath(f'{name}.csv')
        path_csv.touch()
        with path_csv.open('r+', encoding='utf8') as filehandle:
            queue = Queue(
                [QueueItem(**row) for row in csv.DictReader(filehandle)],
                **self.queue_settings.get(name, {}),
            )
            yield queue
            if queue.modified:
                filehandle.seek(0)
                filehandle.truncate(0)
                fields = tuple(field.name for field in dataclasses.fields(QueueItem))
                writer = csv.DictWriter(filehandle, fields)
                writer.writeheader()
                for row in queue.items:
                    writer.writerow(dataclasses.asdict(row, dict_factory=QueueItem.dict_factory))


@dataclasses.dataclass
class QueueItem():
    track_id: str
    track_duration: datetime.timedelta
    owner: str
    start_time: datetime.datetime = None
    id: float = dataclasses.field(default_factory=random.random)

    def __post_init__(self):
        """
        >>> QueueItem('Track1', 60.25, 'Session1', 123456789.123456789, 0.123456789)
        QueueItem(track_id='Track1', track_duration=datetime.timedelta(seconds=60, microseconds=250000), owner='Session1', start_time=123456789.12345679, id=0.123456789)
        """
        self.track_duration = datetime.timedelta(seconds=self.track_duration) if isinstance(self.track_duration, numbers.Number) else self.track_duration
        self.start_time = datetime.datetime.fromtimestamp(self.start_time) if isinstance(self.track_duration, numbers.Number) else self.start_time
        self.id = float(self.id)
    @staticmethod
    def dict_factory(key_values):
        """
        >>> i = QueueItem('Track1', 60.25, 'Session1', 123456789.123456789, 0.123456789)
        >>> dataclasses.asdict(i, dict_factory=QueueItem.dict_factory)
        {'track_id': 'Track1', 'track_duration': 60.25, 'owner': 'Session1', 'start_time': 123456789.12345679, 'id': 0.123456789}
        """
        def _parse(dd):
            k, v = dd
            if isinstance(v, datetime.timedelta):
                v= v.total_seconds()
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
    def move(self, id_source: float, id_destination: float) -> None:
        raise NotImplementedError()
        self._recalculate_start_times()
    def delete(self, id: float) -> None:
        now = self.now
        self.items[:] = [i for i in self.items if (i.start_time and i.start_time < now) or i.id != id]
        self._recalculate_start_times()
    def _recalculate_start_times(self) -> None:
        current = self.current
        future = list(self.future)
        if future and future[0] != current:
            future.insert(0, current)
        for i_prev, i_next in pairwise(future):
            i_next.start_time = i_prev.end_time + self.track_space if i_prev and i_prev.start_time else None
        self.modified = True
