import datetime

from pyramid.decorator import reify
from sqlalchemy import or_, and_
from sqlalchemy.orm.exc import NoResultFound

from externals.lib.misc import now

from . import QUEUE_DUPLICATE, TOKEN_ISSUE_ERROR

from ..model import DBSession
from ..model.model_queue import Queue, QueueItem

from ..views.queue_settings import queue_settings_view, acquire_cache_bucket_func as queue_settings_acquire_cache_bucket_func
from ..views.queue_items import queue_items_view, acquire_cache_bucket_func as queue_items_acquire_cache_bucket_func


class QueueLogic():
    def __init__(self, request):
        self.request = request

    @reify
    def exists(self):
        return DBSession.query(Queue).filter(Queue.id == self.request.context.id).count()

    @reify
    def settings(self):
        return self.request.call_sub_view(queue_settings_view, queue_settings_acquire_cache_bucket_func)['settings']

    @reify
    def duration(self):
        """
        Get total queue length/duration
        will always return a timedelta

        I wanted to rely on only having the 'duration' logic in one place,
        so here I opted to use the cahced API out to get the track duration.
        Long winded, I know. But the complexity of loading the queue, manually
        linking the tracks, then the logic to add with the padding size ...
        Just use the API out
        """
        queue = self.request.call_sub_view(queue_items_view, queue_items_acquire_cache_bucket_func)['queue']
        if queue:
            return queue[-1]['total_duration'] + datetime.timedelta(seconds=queue[-1]['track']['duration'])
        return datetime.timedelta()

    def for_track(self, track_id):
        return self._queue_item_for(self._queue_item_base_query.filter(QueueItem.track_id == track_id))

    def for_performer(self, performer_name):
        return self._queue_item_for(self._queue_item_base_query.filter(QueueItem.performer_name == performer_name))

    @property
    def _queue_item_base_query(self):
        return (
            DBSession.query(QueueItem)
            .filter(or_(
                QueueItem.status == 'pending',
                and_(
                    QueueItem.status == 'played',
                    QueueItem.time_touched >= datetime.datetime.now() - self.request.queue.settings.get('karakara.queue.add.duplicate.time_limit')
                )
            ))
            .order_by(QueueItem.queue_weight)
        )

    def _queue_item_for(self, queue_items_query):
        time_limit = self.request.queue.settings.get('karakara.queue.add.duplicate.time_limit')
        track_limit = self.request.queue.settings.get('karakara.queue.add.duplicate.track_limit')
        performer_limit = self.request.queue.settings.get('karakara.queue.add.duplicate.performer_limit')

        queue_items = queue_items_query.all()

        played = [q for q in queue_items if q.status == 'played']
        pending = [q for q in queue_items if q.status == 'pending']
        track_count = len(played+pending)
        latest_queue_item = queue_items[0] if len(queue_items) else None

        track_status = QUEUE_DUPLICATE.NONE
        if track_limit and track_count >= track_limit:
            track_status = QUEUE_DUPLICATE.THRESHOLD
        elif pending:
            track_status = QUEUE_DUPLICATE.PENDING
        elif played:
            track_status = QUEUE_DUPLICATE.PLAYED

        performer_status = QUEUE_DUPLICATE.NONE
        if performer_limit and track_count >= performer_limit:
            performer_status = QUEUE_DUPLICATE.THRESHOLD

        estimated_next_add_time = datetime.timedelta(0)
        if time_limit and latest_queue_item:
            estimated_next_add_time = time_limit - (now() - latest_queue_item.time_touched)  # time_touched is NOT an acceptable way of measuring this. We need to calculate the estimated track time, but that is really expensive

        return {
            'queue_items': queue_items,
            'played': played,
            'pending': pending,
            'track_status': track_status,
            'track_limit': track_limit,
            'performer_status': performer_status,
            'performer_limit': performer_limit,
            'estimated_next_add_time': estimated_next_add_time,
            'track_count': track_count,
        }
