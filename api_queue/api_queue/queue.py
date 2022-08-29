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
    playtime: datetime.datetime = None
    id: float = dataclasses.field(default_factory=random.random)
    def __post_init__(self):
        self.track_duration = datetime.timedelta(seconds=self.track_duration) if isinstance(self.track_duration, numbers.Number) else self.track_duration
        self.playtime = datetime.datetime.fromordinal(self.playtime) if isinstance(self.track_duration, numbers.Number) else self.playtime
    @property
    def end_time(self):
        if self.playtime:
            return self.playtime + self.track_duration

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
        return (i for i in self.items if i.playtime and i.end_time < now)
    @property
    def future(self) -> Iterator[QueueItem]:
        now = self.now
        return (i for i in self.items if not i.playtime or i.playtime >= now)
    @property
    def current(self) -> QueueItem:
        return self.playing or next(self.future, None)
    @property
    def last(self) -> QueueItem:
        return self.items[-1] if self.items else None
    @property
    def playing(self) -> QueueItem:
        now = self.now
        return next((i for i in self.items if i.playtime and i.playtime <= now and i.end_time > now), None)
    @property
    def is_playing(self) -> bool:
        return self.current and self.current.playtime
    @property
    def end_time(self) -> datetime.datetime:
        if self.last.end_time:
            return self.last.end_time
        def track_duration_reducer(end_time, i):
            end_time += i.track_duration + self.track_space
            return end_time
        return reduce(track_duration_reducer, self.future, self.now)
    def play(self) -> None:
        self.current.playtime = self.now
        self._recalculate_playtimes()
    def stop(self) -> None:
        self.current.playtime = None
        self._recalculate_playtimes()
    def add(self, queue_item: QueueItem) -> None:
        self.items.append(queue_item)
        self._recalculate_playtimes()
    def move(self, id_source: float, id_destination: float) -> None:
        raise NotImplementedError()
        self._recalculate_playtimes()
    def delete(self, id: float) -> None:
        now = self.now
        self.items[:] = [i for i in self.items if (i.playtime and i.playtime < now) or i.id != id]
        self._recalculate_playtimes()
    def _recalculate_playtimes(self) -> None:
        current = self.current
        future = list(self.future)
        if future and future[0] != current:
            future.insert(0, current)
        for i_prev, i_next in pairwise(future):
            i_next.playtime = i_prev.end_time + self.track_space if i_prev and i_prev.playtime else None
