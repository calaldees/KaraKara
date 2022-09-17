import dataclasses
import datetime
from typing import Iterator, Optional
import random
import numbers
from functools import reduce
from itertools import pairwise


# dataclasses are ment to be this cool hip new happening pattern in python
# have I missed the point here? this feels like verbose rubbish for such a simple class
@dataclasses.dataclass
class QueueItem():
    track_id: str
    track_duration: datetime.timedelta
    session_id: str
    performer_name: str
    start_time: Optional[datetime.datetime] = None
    id: int = dataclasses.field(default_factory=lambda:random.randint(0,2**30))

    def __post_init__(self):
        """
        >>> QueueItem('Track1', 60.25, 'Session1', 'test_name', 123456789.123456789, 123456789)
        QueueItem(track_id='Track1', track_duration=datetime.timedelta(seconds=60, microseconds=250000), session_id='Session1', performer_name='test_name', start_time=datetime.datetime(1973, 11, 29, 21, 33, 9, 123457), id=123456789)
        >>> QueueItem('Track1', '60.25', 'Session1', 'test_name', '123456789.123456789', '123456789')
        QueueItem(track_id='Track1', track_duration=datetime.timedelta(seconds=60, microseconds=250000), session_id='Session1', performer_name='test_name', start_time=datetime.datetime(1973, 11, 29, 21, 33, 9, 123457), id=123456789)
        >>> QueueItem('', '', '', '', '', 123456789)
        QueueItem(track_id='', track_duration=datetime.timedelta(0), session_id='', performer_name='', start_time=None, id=123456789)
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
        self.id = int(self.id)
    def asdict(self):
        return dataclasses.asdict(self, dict_factory=self.dict_factory)
    @staticmethod
    def dict_factory(key_values):
        """
        >>> i = QueueItem('Track1', 60.25, 'Session1', 'test_name', 123456789.123456789, 123456789)
        >>> i.asdict()
        {'track_id': 'Track1', 'track_duration': 60.25, 'session_id': 'Session1', 'performer_name': 'test_name', 'start_time': 123456789.123457, 'id': 123456789}
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
    def __init__(self, items: list[QueueItem], settings: dict):
        self.items = items
        self.track_space = settings["track_space"]
        self.modified = False
        self._now: Optional[datetime.datetime] = None
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
    def move(self, id1: int, id2: int) -> None:
        assert {id1, id2} < {i.id for i in self.current_future}|{-1,}, 'move track_ids are not in future track list'
        index1, queue_item = self.get(id1)
        del self.items[index1]
        index2, _ = self.get(id2) if id2 != -1 else (len(self.items), None) # id's are positive. `-1` is a special sentinel value for end of list
        queue_item.start_time = None
        self.items.insert(index2, queue_item)
        self._recalculate_start_times()
    def get(self, id: int) -> tuple[int, QueueItem]:
        return next(((index, queue_item) for index, queue_item in enumerate(self.items) if queue_item.id==id), (None, None))
    def delete(self, id: int) -> None:
        now = self.now
        self.items[:] = [i for i in self.items if (i.start_time and i.start_time < now) or i.id != id]
        self._recalculate_start_times()
    def seek_forwards(self, seconds: float=20) -> None:
        delta = datetime.timedelta(seconds=seconds)
        # if we're in a gap, seek stops at the end of the gap
        if self.current.start_time > self.now:
            if self.now + delta > self.current.start_time:
                self.current.start_time = self.now
            else:
                self.current.start_time -= delta
        # if we're in a track, seek stops at the end of the track
        else:
            if self.now + delta > self.current.end_time:
                self.current.start_time = self.now - self.current.track_duration
                # also adjust the new "current"
                if self.current:
                    self.current.start_time = self.now + self.track_space
            else:
                self.current.start_time -= delta
        self._recalculate_start_times()
    def seek_backwards(self, seconds: float=20) -> None:
        delta = datetime.timedelta(seconds=seconds)
        # if we're in a gap, seek stops at the start of the gap
        if self.current.start_time > self.now:
            if self.now - delta < self.current.start_time - self.track_space:
                self.current.start_time = self.now + self.track_space
            else:
                self.current.start_time += delta
        # if we're in a track, seek stops at the start of the track
        else:
            if self.now - delta < self.current.start_time:
                self.current.start_time = self.now
            else:
                self.current.start_time += delta
        self._recalculate_start_times()
    def skip(self) -> None:
        # seek_forwards will stop at the end of the current track or space
        self.seek_forwards(9999)
    def _recalculate_start_times(self) -> None:
        for i_prev, i_next in pairwise(self.current_future):
            i_next.start_time = i_prev.end_time + self.track_space if i_prev and i_prev.start_time else None
        self.modified = True
