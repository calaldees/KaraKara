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
    """
    >>> qu = Queue([], track_space=datetime.timedelta(seconds=10))
    >>> qu.current
    >>> qu.playing
    >>> qu.add(QueueItem('Track1', 60, 'TestSession1'))
    >>> [i.track_id for i in qu.items]
    ['Track1']
    >>> qu.current.track_id
    'Track1'
    >>> qu.current.playtime
    >>> qu.add(QueueItem('Track2', 60, 'TestSession2'))
    >>> [i.track_id for i in qu.items]
    ['Track1', 'Track2']
    >>> qu.current.track_id
    'Track1'

    Playing state when moving time forward
    >>> qu._now = datetime.datetime.now()
    >>> qu.play()
    >>> qu.playing.track_id
    'Track1'
    >>> qu._now += datetime.timedelta(seconds=30)
    >>> qu.playing.track_id
    'Track1'
    >>> qu._now += datetime.timedelta(seconds=30)
    >>> qu.playing
    >>> qu._now += datetime.timedelta(seconds=30)
    >>> qu.playing.track_id
    'Track2'
    >>> qu._now += datetime.timedelta(seconds=30)
    >>> qu.playing.track_id
    'Track2'
    >>> qu._now += datetime.timedelta(seconds=30)
    >>> qu.playing

    Past tracks
    >>> [i.track_id for i in qu.items]
    ['Track1', 'Track2']
    >>> [i.track_id for i in qu.past]
    ['Track1', 'Track2']
    >>> [i.track_id for i in qu.future]
    []

    Adding + Deleting + Future + current tracks work after played past tracks
    >>> qu.add(QueueItem('Track3', 60, 'TestSession3'))
    >>> qu.add(QueueItem('Track4', 60, 'TestSession4'))
    >>> qu.playing
    >>> qu.current.track_id
    'Track3'
    >>> [i.track_id for i in qu.future]
    ['Track3', 'Track4']
    >>> qu.delete(qu.current.id)
    >>> [i.track_id for i in qu.future]
    ['Track4']
    >>> qu.current.track_id
    'Track4'

    Can't delete past items
    >>> [i.track_id for i in qu.past]
    ['Track1', 'Track2']
    >>> past_track_id = [i for i in qu.past][1].id
    >>> qu.delete(past_track_id)
    >>> [i.track_id for i in qu.past]
    ['Track1', 'Track2']

    Adding tracks while playing populates the playtime
    >>> qu._now += datetime.timedelta(seconds=30)
    >>> qu.playing
    >>> qu.current.track_id
    'Track4'
    >>> qu.play()
    >>> qu.playing.track_id
    'Track4'
    >>> qu._now += datetime.timedelta(seconds=30)
    >>> qu.playing.track_id
    'Track4'
    >>> qu.add(QueueItem('Track5', 60, 'TestSession5'))
    >>> qu.last.track_id
    'Track5'
    >>> qu.last.playtime > qu.now
    True
    >>> qu._now += datetime.timedelta(seconds=60)
    >>> qu.playing.track_id
    'Track5'
    >>> qu._now += datetime.timedelta(seconds=60)
    >>> qu.playing

    Stop functions correctly
    >>> qu.add(QueueItem('Track6', 60, 'TestSession6'))
    >>> qu.add(QueueItem('Track7', 60, 'TestSession7'))
    >>> qu.playing
    >>> qu._now += datetime.timedelta(seconds=60)
    >>> qu.playing
    >>> qu.play()
    >>> qu._now += datetime.timedelta(seconds=30)
    >>> qu.playing.track_id
    'Track6'
    >>> qu.stop()
    >>> qu.playing
    >>> all([i.playtime for i in qu.past])
    True
    >>> [i.playtime for i in qu.future]
    [None, None]
    >>> qu._now += datetime.timedelta(seconds=60)
    >>> qu.playing
    >>> [i.track_id for i in qu.future]
    ['Track6', 'Track7']
    >>> qu.play()
    >>> qu._now += datetime.timedelta(seconds=30)
    >>> qu.playing.track_id
    'Track6'
    >>> qu._now += datetime.timedelta(seconds=60)
    >>> qu.playing.track_id
    'Track7'
    >>> qu._now += datetime.timedelta(seconds=60)
    >>> qu.playing

    >>> last = qu.last
    >>> qu.end_time == last.end_time
    True
    >>> qu.add(QueueItem('Track8', 60, 'TestSession8'))
    >>> qu.add(QueueItem('Track9', 60, 'TestSession9'))
    >>> qu.end_time == qu.now + (datetime.timedelta(seconds=60)*2) + (qu.track_space*2)
    True

    """
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
