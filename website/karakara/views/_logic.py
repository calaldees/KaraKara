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

from karakara.lib.misc import now, json_object_handler
from karakara.model.model_queue import QueueItem
from karakara.model.model_token import PriorityToken

__all__ = [
    'queue_item_for_track', 'QUEUE_DUPLICATE',
    'issue_priority_token',
]



# Constants ----------

class QUEUE_DUPLICATE():
    NONE      = None
    THRESHOLD = 'THRESHOLD'
    PLAYED    = 'PLAYED'
    PENDING   = 'PENDING'
    PERFORMER = 'PERFORMER'


# Methods -----------

def queue_item_base_query(request, DBSession):
    time_limit = request.registry.settings.get('karakara.queue.add.duplicate.time_limit')
    return DBSession.query(QueueItem) \
        .filter(or_(
            QueueItem.status=='pending',
            and_(QueueItem.status=='played', QueueItem.time_touched>=datetime.datetime.now()-time_limit)
        )) \
        .order_by(QueueItem.queue_weight)


def queue_item_for_track(request, DBSession, track_id):
    """
    
    Could be 2 DB querys, both involved in limit setting
    """
    count_limit = request.registry.settings.get('karakara.queue.add.duplicate.count_limit')
    # If we are restricting duplicates then perform additional querys to enforce this.
    
    queue_items = queue_item_base_query(request, DBSession) \
        .filter(QueueItem.track_id==track_id) \
        .all()
    played  = [q for q in queue_items if q.status=='played' ]
    pending = [q for q in queue_items if q.status=='pending']
    
    status  = QUEUE_DUPLICATE.NONE
    if count_limit and len(played+pending) >= count_limit:
        status = QUEUE_DUPLICATE.THRESHOLD
    elif pending:
        status = QUEUE_DUPLICATE.PENDING
    elif played:
        status = QUEUE_DUPLICATE.PLAYED
    
    return {'played':played, 'pending':pending, 'status':status}


def issue_priority_token(request, DBSession):
    # Aquire most recent priority token - if most recent token in past, set recent token to now
    try:
        latest_token = DBSession.query(PriorityToken).filter(PriorityToken.used==False).order_by(PriorityToken.valid_end.desc()).limit(1).one()
        latest_token_end = latest_token.valid_end
    except NoResultFound:
        latest_token_end = None
    if not latest_token_end or latest_token_end < now():
        latest_token_end = now() + get_queue_duration(request)
    
    # Do not issue tokens past the end of the event
    event_end = request.registry.settings.get('karakara.event.end')
    if event_end and latest_token_end > event_end:
        # Unable to issue token as event end
        return None
    
    priority_token_limit = request.registry.settings.get('karakara.queue.add.limit.priority_token')
    if priority_token_limit and latest_token_end > now()+priority_token_limit:
        # Unable to issue token as priority tokens are time limited
        return None
    
    # Do not issue another priority_token if current user alrady has a priority_token
    try:
        priority_token = DBSession.query(PriorityToken) \
                            .filter(PriorityToken.used==False) \
                            .filter(PriorityToken.session_owner==request.session['id']) \
                            .filter(PriorityToken.valid_end>now()) \
                            .one()
        if priority_token:
            return None
    except NoResultFound:
        pass
    
    priority_window = request.registry.settings.get('karakara.queue.add.priority_window')
    
    priority_token = PriorityToken()
    priority_token.session_owner = request.session['id']
    priority_token.valid_start = latest_token_end
    priority_token.valid_end   = latest_token_end + priority_window
    DBSession.add(priority_token)

    #request.response.set_cookie('priority_token', json_cookie);  # WebOb.set_cookie mangles the cookie with m.serialize() - so I rolled my own set_cookie
    json_cookie = json.dumps(priority_token.to_dict(), default=json_object_handler)
    request.response.headerlist.append(('Set-Cookie', 'priority_token={0}; Path=/'.format(json_cookie)))
    
    return priority_token

def consume_priority_token(request, DBSession):
    try:
        token = DBSession.query(PriorityToken) \
            .filter(PriorityToken.used==False) \
            .filter(PriorityToken.session_owner==request.session['id']) \
            .filter(PriorityToken.valid_start<=now(), PriorityToken.valid_end>now()) \
            .one()
        token.used = True
        #request.unset_cookie('priority_token') # may not work with format='redirect'
        request.cookies.pop('priority_token',None)
        #DBSession.delete(token)
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
    from .queue import queue_view # 
    queue = queue_view(request)['data']['queue']
    if queue:
        return queue[-1]['total_duration'] + datetime.timedelta(seconds=queue[-1]['track']['duration'])
    return datetime.timedelta()
