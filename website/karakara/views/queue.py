from pyramid.view import view_config

from . import web, etag, method_delete_router


from ..lib.auto_format    import action_ok, action_error
from ..model              import DBSession
from ..model.model_queue  import QueueItem
from ..model.model_tracks import Track

from sqlalchemy.orm import joinedload, joinedload_all

# Fake Etag placeholder
from ..lib.misc import random_string
queue_instance_id = None
def queue_updated():
    global queue_instance_id
    queue_instance_id = random_string()
queue_updated()
def queue_etag(request):
    global queue_instance_id
    return queue_instance_id + request.session.get('id','') + str(request.session.get('admin',False)) + str(request.session.peek_flash())

#-------------------------------------------------------------------------------
# Queue
#-------------------------------------------------------------------------------

@view_config(route_name='queue', request_method='GET')
@etag(queue_etag)
@web
def queue_view(request):
    """
    view current queue
    """
    queue = DBSession.query(QueueItem).filter(QueueItem.status=='pending').options(joinedload_all('track.attachments')).all()
    queue = [queue_item.to_dict('full') for queue_item in queue]
    return action_ok(data={'list':queue})


@view_config(route_name='queue', request_method='POST')
@web
def queue_add(request):
    """
    Add items to end of queue
    """
    
    queue_item = QueueItem()
    
    for key,value in request.params.items():
        if hasattr(queue_item, key):
            setattr(queue_item, key, value)
    
    queue_item.session_owner  = request.session['id']
    DBSession.add(queue_item)
    
    queue_updated() # Invalidate Cache
    
    return action_ok(message='track queued')


@view_config(route_name='queue', custom_predicates=(method_delete_router, lambda info,request: request.params.get('queue_item.id')) ) #request_method='POST',
@web
def queue_del(request):
    """
    Remove items from the queue
    
    check session owner or admin
    state can be passed as "complete" to mark track as played
    """
    queue_item = DBSession.query(QueueItem).get(request.params['queue_item.id'])

    if not queue_item:
        raise action_error(message='invalid queue_item.id')
    if not request.session.get('admin',False) and queue_item.session_owner != request.session['id']:
        raise action_error(message='you are not the owner of this queue_item')

    #DBSession.delete(queue_item)
    queue_item.status = request.params.get('status','removed')
    
    queue_updated() # Invalidate Cache
    
    return action_ok(message='queue_item status changed')


@view_config(route_name='queue', request_method='PUT')
@web
def queue_update(request):
    """
    Used to touch queed items
    
    check session owner or admin
    """
    queue_item = DBSession.query(QueueItem).get(request.params['queue_item.id'])

    if not queue_item:
        raise action_error(message='invalid queue_item.id')
    if request.session.get('admin',False) or queue_item.session_owner != request.session['id']:
        raise action_error(message='you are not the owner of this queue_item')

    # Update any params to the db
    for key,value in request.params.items():
        if hasattr(queue_item, key):
            setattr(queue_item, key, value)
    queue_item.touched = datetime.datetime.now() # Update touched timestamp
    
    queue_updated() # Invalidate Cache
    
    return action_ok(message='queue_item updated')
