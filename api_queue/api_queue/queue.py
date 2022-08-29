import contextlib
import dataclasses
import datetime
import random
import numbers
from functools import reduce
from itertools import pairwise
from typing import Iterator

class QueueManager():
    def __init__(self):
        pass
    @contextlib.asynccontextmanager
    def async_queue_modify_context(self, name):
        # open
        yield None
        # save
        # push to mqtt?

@dataclasses.dataclass
class QueueItem():
    track_id: str
    track_duration: datetime.timedelta
    owner: str
    start_time: datetime.datetime = None
    id: float = dataclasses.field(default_factory=random.random)
    def __post_init__(self):
        self.track_duration = datetime.timedelta(seconds=self.track_duration) if isinstance(self.track_duration, numbers.Number) else self.track_duration
        self.start_time = datetime.datetime.fromordinal(self.start_time) if isinstance(self.track_duration, numbers.Number) else self.start_time
    @property
    def end_time(self):
        if self.start_time:
            return self.start_time + self.track_duration

class Queue():
    def __init__(self, items: list[QueueItem], track_space: datetime.timedelta):
        self.items = items
        self.track_space = track_space
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
