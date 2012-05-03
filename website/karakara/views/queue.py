from pyramid.view import view_config

from ..lib.auto_format    import auto_format_output, action_ok
from ..model              import DBSession


#-------------------------------------------------------------------------------
# Queue
#-------------------------------------------------------------------------------

@view_config(route_name='queue', request_method='GET')
@auto_format_output
def queue_view(request):
    """
    view current queue
    """
    return action_ok()

@view_config(route_name='queue', request_method='POST')
@auto_format_output
def queue_add(request):
    """
    Add items to end of queue
    """
    return action_ok()

@view_config(route_name='queue', request_method='DELETE')
@auto_format_output
def queue_del(request):
    """
    Remove items from the queue
    
    check session owner or admin
    """
    return action_ok()

@view_config(route_name='queue', request_method='PUT')
@auto_format_output
def queue_update(request):
    """
    Used to touch queed items
    
    check session owner or admin
    """
    return action_ok()
