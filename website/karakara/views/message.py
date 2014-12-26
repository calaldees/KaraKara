from decorator import decorator

from pyramid.view import view_config

from . import web, action_ok, action_error, request_from_args

from ..model.model_messages import Message


import logging
log = logging.getLogger(__name__)

# Decorator --------------------------------------------------------------------

def overlay_messages():
    """
    Decorator to overlay pending messages onto return
    """
    def _overlay_messages(target, *args, **kwargs):
        request = request_from_args(args)
        if 'internal_request' in request.matchdict:  # Abort if internal call
            return target(*args, **kwargs)

        #log.debug('Overlay messages test')
        result = target(*args, **kwargs)

        return result

    return decorator(_overlay_messages)


#-------------------------------------------------------------------------------
# Messages
#-------------------------------------------------------------------------------

@view_config(route_name='message', request_method='GET')
@web
def message_view(request):
    return action_ok()


@view_config(route_name='message', request_method='POST')
@web
def message_add(request):
    return action_ok()
