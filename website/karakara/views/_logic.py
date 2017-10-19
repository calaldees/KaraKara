"""
Common View Logic
  - common place for logic and complex querys that often appear duplicated across the system
  
The rational behind placing these in the views is because they can acess pyramid settings.
Acess to settings does not belong in the model
"""
import datetime
import json

from sqlalchemy import or_, and_
from sqlalchemy.orm.exc import NoResultFound

from externals.lib.misc import now, json_object_handler

from karakara.model.model_queue import QueueItem
from karakara.model.model_priority_token import PriorityToken

import logging
log = logging.getLogger(__name__)


__all__ = [
    'queue_item_for_performer',
    'queue_item_for_track',
    'QUEUE_DUPLICATE',
    'TOKEN_ISSUE_ERROR',
    'issue_priority_token',
]


# Constants ----------

class QUEUE_DUPLICATE():
    NONE = None
    THRESHOLD = 'THRESHOLD'
    PLAYED = 'PLAYED'
    PENDING = 'PENDING'
    PERFORMER = 'PERFORMER'


class TOKEN_ISSUE_ERROR(object):
    NONE = None
    EVENT_END = 'EVENT_END'
    TOKEN_LIMIT = 'TOKEN_LIMIT'
    TOKEN_ISSUED = 'TOKEN_ISSUED'


# Methods -----------

def _queue_item_base_query(request, DBSession):
    time_limit = request.registry.settings.get('karakara.queue.add.duplicate.time_limit')
    return DBSession.query(QueueItem) \
        .filter(or_(
            QueueItem.status == 'pending',
            and_(QueueItem.status == 'played', QueueItem.time_touched >= datetime.datetime.now()-time_limit)
        )) \
        .order_by(QueueItem.queue_weight)


def queue_item_for_performer(request, DBSession, performer_name):
    return _queue_item_for(
        request,
        _queue_item_base_query(request, DBSession).filter(QueueItem.performer_name == performer_name)
    )


def queue_item_for_track(request, DBSession, track_id):
    return _queue_item_for(
        request,
        _queue_item_base_query(request, DBSession).filter(QueueItem.track_id == track_id)
    )


def _queue_item_for(request, queue_items_query):
    time_limit = request.registry.settings.get('karakara.queue.add.duplicate.time_limit')
    track_limit = request.registry.settings.get('karakara.queue.add.duplicate.track_limit')
    performer_limit = request.registry.settings.get('karakara.queue.add.duplicate.performer_limit')

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


def issue_priority_token(request, DBSession):
    priority_window = request.registry.settings.get('karakara.queue.add.limit.priority_window')

    # Aquire most recent priority token - if most recent token in past, set recent token to now
    try:
        latest_token = DBSession.query(PriorityToken).filter(PriorityToken.used==False).order_by(PriorityToken.valid_end.desc()).limit(1).one()
        latest_token_end = latest_token.valid_end
    except NoResultFound:
        latest_token_end = None
    if not latest_token_end or latest_token_end < now():
        # When issueing the first priority token
        latest_token_end = now() + priority_window  # get_queue_duration(request) # Adding entire queue here was unnessisary.

    # Do not issue tokens past the end of the event
    event_end = request.registry.settings.get('karakara.event.end')
    if event_end and latest_token_end > event_end:
        # Unable to issue token as event end
        log.debug('priority_token rejected - event end')
        return TOKEN_ISSUE_ERROR.EVENT_END

    priority_token_limit = request.registry.settings.get('karakara.queue.add.limit.priority_token')
    if priority_token_limit and latest_token_end > now()+priority_token_limit:
        # Unable to issue token as priority tokens are time limited
        log.debug('priority_token rejected - token limit')
        return TOKEN_ISSUE_ERROR.TOKEN_LIMIT

    # Do not issue another priority_token if current user alrady has a priority_token
    try:
        priority_token = DBSession.query(PriorityToken) \
                            .filter(PriorityToken.used==False) \
                            .filter(PriorityToken.session_owner==request.session['id']) \
                            .filter(PriorityToken.valid_end>now()) \
                            .one()
        if priority_token:
            log.debug('priority_token rejected - existing token')
            return TOKEN_ISSUE_ERROR.TOKEN_ISSUED
    except NoResultFound:
        pass

    # Issue the new token
    priority_token = PriorityToken()
    priority_token.session_owner = request.session['id']
    priority_token.valid_start = latest_token_end
    priority_token.valid_end = latest_token_end + priority_window
    DBSession.add(priority_token)

    # TODO: replace with new one in lib
    #request.response.set_cookie('priority_token', json_cookie);  # WebOb.set_cookie mangles the cookie with m.serialize() - so I rolled my own set_cookie
    priority_token_dict = priority_token.to_dict()
    priority_token_dict.update({
        'server_datetime': now(),  # The client datetime and server datetime may be out. we need to return the server time so the client can calculate the difference
    })
    json_cookie = json.dumps(priority_token_dict, default=json_object_handler)
    request.response.headerlist.append(('Set-Cookie', 'priority_token={0}; Path=/'.format(json_cookie)))

    log.debug('priority_token issued')
    return priority_token


def consume_priority_token(request, DBSession):
    try:
        token = DBSession.query(PriorityToken) \
            .filter(PriorityToken.used == False) \
            .filter(PriorityToken.session_owner == request.session['id']) \
            .filter(PriorityToken.valid_start <= now(), PriorityToken.valid_end > now()) \
            .one()
        token.used = True
        request.response.delete_cookie('priority_token')
        log.debug('priority_token consumed')
        return True
    except NoResultFound:
        return False


def get_queue_duration(request):
    """
    Get total queue length/duration
    will always return a timedelta

    BOLLOX! Had to prevent circular dependency.
    I wanted to rely on only having the 'duration' logic in one place,
    so here I opted to use the cahced API out to get the track duration.
    Long winded, I know. But the complexity of loading the queue, manually
    linking the tracks, then the logic to add with the padding size ...
    Just use the API out
    """
    from .queue import queue_view
    queue = queue_view(request)['data']['queue']
    if queue:
        return queue[-1]['total_duration'] + datetime.timedelta(seconds=queue[-1]['track']['duration'])
    return datetime.timedelta()
