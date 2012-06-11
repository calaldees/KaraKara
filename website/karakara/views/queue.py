from pyramid.view import view_config

from . import base

from ..lib.auto_format    import auto_format_output, action_ok
from ..model              import DBSession
from ..model.model_queue  import QueueItem


#-------------------------------------------------------------------------------
# Queue
#-------------------------------------------------------------------------------

@view_config(route_name='queue', request_method='GET')
@base
@auto_format_output
def queue_view(request):
    """
    view current queue
    """
    queue = DBSession.query(QueueItem).filter(QueueItem.status=='pending').all()
    queue = [queue_item.to_dict() for queue_item in queue]
    return action_ok(data={'list':queue})

@view_config(route_name='queue', request_method='POST')
@base
@auto_format_output
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
    
    return action_ok(message='track queued')

@view_config(route_name='queue', request_method='DELETE')
@base
@auto_format_output
def queue_del(request):
    """
    Remove items from the queue
    
    check session owner or admin
    """
    queue_item = DBSession.query(QueueItem).get(request.params['queue_item.id'])

    if not queue_item:
        raise action_error(message='invalid queue_item.id')
    if request.session.get('admin',False) or queue_item.session_owner != request.session['id']:
        raise action_error(message='you are not the owner of this queue_item')

    #DBSession.delete(queue_item)
    queue_item.status = 'removed'
    
    return action_ok(message='queue_item deleted')

@view_config(route_name='queue', request_method='PUT')
@base
@auto_format_output
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
    
    return action_ok(message='queue_item updated')
