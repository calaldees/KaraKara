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

from karakara.lib.misc import now
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


# Methods -----------

def queue_item_for_track(request, DBSession, track_id):
    """
    
    Could be 2 DB querys, both involved in limit setting
    """
    count_limit = request.registry.settings.get('karakara.queue.add.duplicate.count_limit')
    time_limit  = request.registry.settings.get('karakara.queue.add.duplicate.time_limit')
    # If we are restricting duplicates then perform additional querys to enforce this.
    
    queue_items = DBSession.query(QueueItem) \
        .filter(QueueItem.track_id==track_id) \
        .filter(or_(
            QueueItem.status=='pending',
            and_(QueueItem.status=='played', QueueItem.time_touched>=datetime.datetime.now()-time_limit)
        )) \
        .order_by(QueueItem.queue_weight) \
        .all()
    played  = [q for q in queue_items if q.status=='played' ]
    pending = [q for q in queue_items if q.status=='pending']
    
    status  = QUEUE_DUPLICATE.NONE
    if count_limit and len(played+pending) > count_limit:
        status = QUEUE_DUPLICATE.THRESHOLD
    elif pending:
        status = QUEUE_DUPLICATE.PENDING
    elif played:
        status = QUEUE_DUPLICATE.PLAYED

    return {'played':played, 'pending':pending, 'status':status}


def issue_priority_token(request, DBSession):
    # Aquire most recent priority token
    try:
        latest_token = DBSession.query(PriorityToken).filter(PriorityToken.used==False).order_by(PriorityToken.end.desc()).limit(1).one()
        latest_token_end = latest_token.end
    except NoResultFound:
        latest_token_end = now()
    
    # Do not issue tokens past the end of the event
    event_end = request.registry.settings.get('karakara.event.end')
    if event_end and latest_token_end > event_end:
        # Unable to issue token as event end
        return None
    
    priority_window = request.registry.settings.get('karakara.queue.add.priority_window')
    
    priority_token = PriorityToken()
    priority_token.session_owner = request.session['id']
    priority_token.start = latest_token_end
    priority_token.end   = latest_token_end + priority_window
    DBSession.add(priority_token)

    request.response.set_cookie('priority_token',json.dumps(priority_token.to_dict()));
    
    return priority_token
    


def get_priority_token(request, DBSession):
    session_owner = request.session['id']
    tokens = DBSession.query(PriorityToken) \
        .filter(PriorityToken.session_owner==session_owner) \
        .filter(PriorityToken.start>=now, PriorityToken.end<now) \
        .all()
    if tokens:
        #DBSession.delete(token[0])
        return tokens[0]
    return None
