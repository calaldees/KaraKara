"""
Common View Logic
  - common place for logic and complex querys that often appear duplicated across the system
  
The rational behind placing these in the views is because they can acess pyramid settings.
Acess to settings does not belong in the model
"""
import datetime
from sqlalchemy import or_, and_

from karakara.model.model_queue import QueueItem


__all__ = [
    'queue_item_for_track', 'QUEUE_DUPLICATE',
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


