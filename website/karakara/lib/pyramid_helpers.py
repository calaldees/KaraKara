import datetime
import dateutil.parser

import pyramid.request
import pyramid.registry
from pyramid.httpexceptions import exception_response

from decorator import decorator


import logging
log = logging.getLogger(__name__)



def request_from_args(args):
    # Extract request object from args
    for arg in args:
        if isinstance(arg, pyramid.request.Request):
            return arg
    raise Exception('no pyramid.request.Request in args')


# TODO: cahce decorator to store plain python dict returns
# TODO: etag should be the cache key - maybe rename method?


def _etag_render_func_default(request):
    return "-".join([
        request.path_qs,
        normalize_datetime(accuracy=request.registry.settings.get('server.etag.expire')).ctime(),
        # request.POST ??,
        # request.session_id ??,
    ])

def etag(etag_render_func=_etag_render_func_default):
    """
    eTag decorator
    
    use:
    
    @etag()
    def my_route_view(request):
        pass
    
    by default this will use the request.route_qs + expire time as the etag
    
    You can specify a function to generate an etag string, this is passed the single argument 'request'
    
    @etag(lambda request: request.path_qs)
    def my_route_view(request):
        pass
    
    TODO: Only trigger on top level request
    """
    def etag(target, *args, **kwargs):
        request = request_from_args(args)
        
        # Abort if internal call
        if 'internal_request' in request.matchdict:
            return target(*args, **kwargs)
        
        etag_enabled = request.registry.settings.get('server.etag.enabled')
        
        if etag_enabled:
            etag = etag_render_func(request)
            if etag and etag in request.if_none_match:
                log.debug('etag matched - aborting render - %s' % etag)
                raise exception_response(304)
        
        result = target(*args, **kwargs) # Execute the wrapped function
        
        if etag_enabled:
            log.debug('etag set - %s' % etag)
            result.etag = etag
        
        return result
    return decorator(etag)
