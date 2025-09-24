import typing as t
from functools import partial
import datetime

from .queue_model import Queue, QueueItem


class QueueValidationError(Exception):
    pass


def queue_updated_actions(queue: Queue):
    validate_queue(queue)
    if queue.settings.auto_reorder_queue:
        reorder(queue)


def validate_queue(queue: Queue):
    """
    Check event start
    Check event end
    Check duplicate performer
    Check duplicate tracks
    Check performer name in performer name list
    """

    _start = queue.settings.validation_event_start_datetime
    if _start and queue.now < _start:
        raise QueueValidationError(f"Event starts at {_start}")

    _end = queue.settings.validation_event_end_datetime
    if _end and queue.end_time > _end:
        raise QueueValidationError(f"Queue is full all the way until {_end}")

    queue_last = queue.last  # This is track that has been proposed to be added (not saved to disk yet)
    if not queue_last:
        return  # No tracks to validate - no need to proceed with further validation

    if _valid_performer_names := queue.settings.validation_performer_names:
        if queue_last.performer_name not in _valid_performer_names:
            raise QueueValidationError(f"{queue_last.performer_name} is not a valid performer_name for this event")

    if _performer_timedelta := None:  # queue.settings.validation_duplicate_performer_timedelta
        raise NotImplementedError("TODO: finish this feature")
        epoch = queue.now - _performer_timedelta

        def _filter(queue_item: QueueItem) -> bool:
            assert queue_item is not None
            return (
                queue_item.performer_name == queue_last.performer_name
                and queue_item.start_time > epoch
                and queue_item != queue_last
            )

        if tuple(filter(_filter, queue.items)):
            return f"Duplicated performer {queue_last.performer_name} within {_performer_timedelta}"

    if _track_timedelta := None:  # queue.settings.validation_duplicate_track_timedelta:
        raise NotImplementedError("TODO: finish this feature")
        epoch = queue.now - _track_timedelta

        def _filter(queue_item: QueueItem) -> bool:
            assert queue_item is not None
            return (
                queue_item.track_id == queue_last.track_id
                and queue_item.start_time > epoch
                and queue_item != queue_last
            )

        if tuple(filter(_filter, queue.items)):
            return f"Duplicated track {queue_last.performer_name} within {_track_timedelta}"


def _rank(queue: Queue, queue_item: QueueItem) -> float:
    """
    negative == sooner
    positive == later

    Time since queued
    Time since last song
    Duration of sung songs (decayed with time ago)
    """

    def _minuets(t: datetime.timedelta) -> float:
        return t.total_seconds() / 60

    def _minuets_ago(d: datetime.datetime) -> float:
        return _minuets(queue.now - d)

    def _hours_ago(d: datetime.datetime) -> float:
        return _minuets_ago(d) / 60

    added_minuets_ago = _minuets_ago(queue_item.added_time)

    queued_by_this_performer: t.Sequence[QueueItem] = tuple(
        filter(
            lambda i: i.performer_name == queue_item.performer_name
            and i.added_time < queue_item.added_time
            and _hours_ago(i.added_time) < 3,
            queue.items,
        )
    )

    def _sang_ago_score(i: QueueItem) -> float:
        if i.start_time:
            # the start_time could be hypothetical (e.g: it has not been sung, but is scheduled/estimated to be start_time)
            sang_hours_ago = _hours_ago(i.start_time)
            # if you sang a single 4 minuet song 1 hour ago
            # added_minuets_ago will rise linearly with time while this rank decays with time
            # for a 20min since the last sang track = ((1/0.35) * 4min * 5) = 57 is equivalent to 60min in the queue
            return (1 / sang_hours_ago) * _minuets(i.track_duration) * 5
        # need thought - it's in the queue, but has no start_time, so the queue is currently paused
        # the queue could be reordered, so we apply a static penalty
        # I don't even know if this is needed
        return _minuets(i.track_duration) * 2

    sang_ago_penalty = sum(map(_sang_ago_score, queued_by_this_performer))

    # print(f'{queue_item.track_id=}: {sang_ago_penalty=} - {added_minuets_ago=}')
    return sang_ago_penalty - added_minuets_ago


def reorder(queue: Queue):
    if not (queue_item_current := queue.current):
        return  # TODO: if not 'playing', no reordering? Check this
    # Only reorder tracks out of view of users (>coming_soon_track_count) - leave the rest of the queue alone
    reorder_from_index = queue.items.index(queue_item_current) + queue.settings.coming_soon_track_count
    queue.items[reorder_from_index:] = sorted(queue.items[reorder_from_index:], key=partial(_rank, queue))
