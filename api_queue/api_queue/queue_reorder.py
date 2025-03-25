from functools import partial
import datetime
from numbers import Number
import typing as t

from .queue_model import Queue, QueueItem


def _rank(queue: Queue, queue_item: QueueItem) -> Number:
    """
    negative == sooner
    positive == later

    Time since queued
    Time since last song
    Duration of sung songs (decayed with time ago)
    """
    def _minuets(t: datetime.timedelta):
        return t.total_seconds()/60 if t else None
    def _minuets_ago(d: datetime.datetime):
        return _minuets(queue.now - d) if d else None
    def _hours_ago(d: t.Optional[datetime.datetime]):
        return _minuets_ago(d)/60 if d else None

    added_minuets_ago = _minuets_ago(queue_item.added_time)

    # All tracks queued by this performer
    queued = tuple(filter(
        lambda i:
            i.performer_name==queue_item.performer_name
            and
            i.added_time < queue_item.added_time
            and
            _hours_ago(i.added_time) < 3
        ,
        queue.items
    ))

    def _sang_ago_score(i: QueueItem):
        sang_hours_ago = _hours_ago(i.start_time)  # the start_time could be hypothetical (e.g: it has not been sung, but is scheduled/estimated to be start_time)
        if sang_hours_ago:
            # if you sang a single 4 miuet song 1 hour ago
            # added_minuets_ago will rise linearly with time while this rank decays with time
            # for a 20min since the last sang track = ((1/0.35) * 4min * 5) = 57 is equivalent to 60min in the queue
            return (1/sang_hours_ago) * _minuets(i.track_duration) * 5
        return _minuets(i.track_duration) * 2  # need thought - it's in the queue, but has no start_time, so the queue is currently paused  # the queue could be reordered, so we apply a static penalty  # I don't even know if this is needed
    sang_ago_penalty = sum(map(_sang_ago_score, queued))

    #print(f'{queue_item.track_id=}: {sang_ago_penalty=} - {added_minuets_ago=}')
    return sang_ago_penalty - added_minuets_ago


def reorder(queue: Queue):
    queue_item_current = queue.current
    if not queue_item_current:
        return
    reorder_index = queue.items.index(queue_item_current) + queue.settings.coming_soon_track_count
    queue.items[reorder_index:] = sorted(queue.items[reorder_index:], key=partial(_rank, queue)) # type: ignore[arg-type]
