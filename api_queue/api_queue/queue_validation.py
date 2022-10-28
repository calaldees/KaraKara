from ._utils import IteratorCombine
from .queue_model import Queue


def default(queue: Queue):
    """
    Check event start
    Check event end
    Check duplicate performer
    Check duplicate tracks
    Check performer name in performer name list
    """

    _start = queue.settings["validation_event_start_datetime"]
    if _start and queue.now < _start:
            return f"event starts at {_start}"

    _end = queue.settings["validation_event_end_datetime"]
    if _end and queue.end_time > _end:
            return f"Unable to queue track as the event is ending at {_end}"

    queue_last = queue.last

    _performer_timedelta = queue.settings["validation_duplicate_performer_timedelta"]
    if _performer_timedelta:
        epoch = queue.now - _performer_timedelta
        if tuple(IteratorCombine()
            .filter(lambda queue_item: queue_item.performer_name == queue_last.performer_name)
            .filter(lambda queue_item: queue_item.start_time > epoch)
            .filter(lambda queue_item: queue_item != queue_last)
            .process(queue.items)
        ):
            return f"duplicated performer {queue_last.performer_name} within {_performer_timedelta}"

    _track_timedelta = queue.settings["validation_duplicate_track_timedelta"]
    if _track_timedelta:
        epoch = queue.now - _track_timedelta
        if tuple(IteratorCombine()
            .filter(lambda queue_item: queue_item.track_id == queue_last.track_id)
            .filter(lambda queue_item: queue_item.start_time > epoch)
            .filter(lambda queue_item: queue_item != queue_last)
            .process(queue.items)
        ):
            return f"duplicated track {queue_last.performer_name} within {_track_timedelta}"

    _valid_performer_names = queue.settings["validation_performer_names"]
    if _valid_performer_names:
        if queue_last.performer_name not in _valid_performer_names:
            return f"{queue_last.performer_name} is not a valid performer_name for this event"
