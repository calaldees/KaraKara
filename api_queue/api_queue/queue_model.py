import dataclasses
import datetime
import typing as t
import random
from functools import reduce
from itertools import pairwise

from .settings_manager import QueueSettings
from .type_parsers import parse_datetime, parse_timedelta


# dataclasses are ment to be this cool hip new happening pattern in python
# have I missed the point here? this feels like verbose rubbish for such a simple class
@dataclasses.dataclass
class QueueItem:
    @staticmethod
    def _now():
        return datetime.datetime.now(tz=datetime.timezone.utc)

    track_id: str
    track_duration: datetime.timedelta
    session_id: str
    performer_name: str
    start_time: datetime.datetime | None = None
    id: int = dataclasses.field(default_factory=lambda: random.randint(0, 2**30))
    added_time: datetime.datetime = dataclasses.field(default_factory=_now)
    debug_str: str | None = None

    def __post_init__(self):
        """
        >>> QueueItem('Track1', 60.25, 'Session1', 'test_name', 123456789.123456789, 123456789, 111111111.111111111)
        QueueItem(track_id='Track1', track_duration=datetime.timedelta(seconds=60, microseconds=250000), session_id='Session1', performer_name='test_name', start_time=datetime.datetime(1973, 11, 29, 21, 33, 9, 123457, tzinfo=datetime.timezone.utc), id=123456789, added_time=datetime.datetime(1973, 7, 10, 0, 11, 51, 111111, tzinfo=datetime.timezone.utc), debug_str=None)

        >>> QueueItem('Track1', '60.25', 'Session1', 'test_name', '1973-11-29 21:33:09.123457', '123456789', 111111111.111111111)
        QueueItem(track_id='Track1', track_duration=datetime.timedelta(seconds=60, microseconds=250000), session_id='Session1', performer_name='test_name', start_time=datetime.datetime(1973, 11, 29, 21, 33, 9, 123457, tzinfo=datetime.timezone.utc), id=123456789, added_time=datetime.datetime(1973, 7, 10, 0, 11, 51, 111111, tzinfo=datetime.timezone.utc), debug_str=None)

        >>> queue_item = QueueItem('', '', '', '', '')
        >>> type(queue_item.track_duration)
        <class 'datetime.timedelta'>
        >>> type(queue_item.id)
        <class 'int'>
        >>> type(queue_item.added_time)
        <class 'datetime.datetime'>
        >>> queue_item.added_time.year >= 2023
        True
        """
        self.id = int(self.id)
        self.track_duration = parse_timedelta(self.track_duration) or datetime.timedelta(0)
        self.start_time = parse_datetime(self.start_time)
        self.added_time = parse_datetime(self.added_time) or self._now()

    def asdict(self):
        return dataclasses.asdict(self, dict_factory=self.dict_factory)

    @staticmethod
    def dict_factory(key_values):
        """
        >>> i = QueueItem('Track1', 60.25, 'Session1', 'test_name', 123456789.123456789, 123456789, 111111111.111111111)
        >>> i.asdict()
        {'track_id': 'Track1', 'track_duration': 60.25, 'session_id': 'Session1', 'performer_name': 'test_name', 'start_time': 123456789.123457, 'id': 123456789, 'added_time': 111111111.111111, 'debug_str': None}
        """

        def _to_base_types(dd):
            k, v = dd
            if isinstance(v, datetime.timedelta):
                v = v.total_seconds()
            elif isinstance(v, datetime.datetime):
                v = v.timestamp()
            return (k, v)

        return dict(map(_to_base_types, key_values))

    @property
    def end_time(self) -> datetime.datetime | None:
        if self.start_time:
            return self.start_time + self.track_duration
        return None

    @property
    def time_since_queued(self) -> datetime.timedelta:
        return self._now() - self.added_time


class Queue:
    def __init__(self, items: list[QueueItem], settings: QueueSettings):
        self.items = items
        self.settings = settings
        self.modified = False
        self._now: datetime.datetime | None = None

    @property
    def track_space(self) -> datetime.timedelta:
        return self.settings.track_space

    @property
    def now(self) -> datetime.datetime:
        return self._now or datetime.datetime.now(tz=datetime.timezone.utc)

    @property
    def past(self) -> t.Iterable[QueueItem]:
        now = self.now
        return (i for i in self.items if i.end_time and i.end_time < now)

    @property
    def future(self) -> t.Iterable[QueueItem]:
        now = self.now
        return (i for i in self.items if not i.start_time or i.start_time >= now)

    @property
    def current(self) -> QueueItem | None:
        return self.playing or next(iter(self.future), None)

    @property
    def current_future(self) -> t.Iterable[QueueItem]:
        # fugly mess - you can do this in less lines
        current = self.current
        future = list(self.future)
        if current and future and future[0] != current:
            future.insert(0, current)
        return future

    @property
    def last(self) -> QueueItem | None:
        return self.items[-1] if self.items else None

    @property
    def playing(self) -> QueueItem | None:
        now = self.now
        return next(
            (i for i in self.items if i.start_time and i.start_time <= now and i.end_time and i.end_time > now),
            None,
        )

    @property
    def is_playing(self) -> bool:
        return bool(self.current and self.current.start_time)

    @property
    def end_time(self) -> datetime.datetime:
        if self.last and self.last.end_time:
            return self.last.end_time

        def track_duration_reducer(end_time: datetime.datetime, i: QueueItem) -> datetime.datetime:
            end_time += i.track_duration + self.track_space
            return end_time

        return reduce(track_duration_reducer, self.future, self.now)

    def play_one(self, immediate=False) -> None:  # Alias for play(continuous=False)
        self.play(continuous=False, immediate=immediate)

    def play(self, continuous=True, immediate=False) -> None:
        if self.current:
            if immediate:
                self.current.start_time = self.now
            else:
                # Set the current track to start playing slightly in
                # the future, to give all the clients a chance to get
                # the message
                self.current.start_time = self.now + datetime.timedelta(seconds=1)
        if continuous:
            self._recalculate_start_times()

    def stop(self) -> None:
        if current := self.current:
            current.start_time = None
            self._recalculate_start_times()

    def add(self, queue_item: QueueItem) -> None:
        self.items.append(queue_item)
        self._recalculate_start_times()

    def move(self, id1: int, id2: int) -> None:
        assert {id1, id2} < {i.id for i in self.current_future} | {
            -1,
        }, "move track_ids are not in future track list"
        index1, queue_item = self.get(id1)
        assert index1 is not None
        assert queue_item is not None
        del self.items[index1]
        index2, _ = (
            self.get(id2) if id2 != -1 else (len(self.items), None)
        )  # id's are positive. `-1` is a special sentinel value for end of list
        assert index2 is not None
        queue_item.start_time = None
        self.items.insert(index2, queue_item)
        self._recalculate_start_times()

    def get(self, id: int) -> tuple[int, QueueItem] | tuple[None, None]:
        return next(
            ((index, queue_item) for index, queue_item in enumerate(self.items) if queue_item.id == id),
            (None, None),
        )

    def delete(self, id: int) -> None:
        if current := self.current:
            # If deleting current item and current item is queued for future playback
            if current.id == id and current.start_time:
                self.stop()
        now = self.now
        self.items[:] = [i for i in self.items if (i.start_time and i.start_time < now) or i.id != id]
        self._recalculate_start_times()

    def seek_forwards(self, seconds: float = 20) -> None:
        if not self.current or not self.current.start_time or not self.current.end_time:
            return
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

    def seek_backwards(self, seconds: float = 20) -> None:
        if not self.current or not self.current.start_time or not self.current.end_time:
            return
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
        if self.current:
            self.delete(self.current.id)

    def _recalculate_start_times(self) -> None:
        for i_prev, i_next in pairwise(self.current_future):
            i_next.start_time = i_prev.end_time + self.track_space if i_prev and i_prev.start_time else None  # type: ignore
        self.modified = True
