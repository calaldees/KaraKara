from .queue_model import Queue, QueueItem


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
    if not queue_last:
        return  # No tracks to validate

    _valid_performer_names = queue.settings["validation_performer_names"]
    if _valid_performer_names:
        if queue_last.performer_name not in _valid_performer_names:
            return f"{queue_last.performer_name} is not a valid performer_name for this event"

    _performer_timedelta = queue.settings["validation_duplicate_performer_timedelta"]
    if _performer_timedelta:
        raise NotImplementedError('TODO: finish this feature')
        epoch = queue.now - _performer_timedelta
        def _filter(queue_item: QueueItem) -> bool:
            assert queue_item is not None
            return (
                queue_item.performer_name == queue_last.performer_name and
                queue_item.start_time > epoch and
                queue_item != queue_last
            )
        if tuple(filter(_filter, queue.items)):
            return f"duplicated performer {queue_last.performer_name} within {_performer_timedelta}"

    _track_timedelta = queue.settings["validation_duplicate_track_timedelta"]
    if _track_timedelta:
        raise NotImplementedError('TODO: finish this feature')
        epoch = queue.now - _track_timedelta
        def _filter(queue_item: QueueItem) -> bool:
            assert queue_item is not None
            return (
                queue_item.track_id == queue_last.track_id and
                queue_item.start_time > epoch and
                queue_item != queue_last
            )
        if tuple(filter(_filter, queue.items)):
            return f"duplicated track {queue_last.performer_name} within {_track_timedelta}"
