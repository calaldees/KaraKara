import datetime
import dateutil.parser

import pyramid.request
import pyramid.registry
from pyramid.httpexceptions import exception_response

from decorator import decorator

from .misc import normalize_datetime

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


def _generate_cache_key_default(request):
    """
    """
    return "-".join([
        request.path_qs,
        normalize_datetime(accuracy=request.registry.settings.get('server.etag.expire')).ctime(), #if normalize_datetime returns None, this dies hard. Fix it!
        # request.POST ??,
        # request.session_id ??,
    ])

def etag(generate_cache_key=_generate_cache_key_default):
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
    
    the generator function can raise a LookupError if the return is not cacheable
    """
    def etag(target, *args, **kwargs):
        request = request_from_args(args)
        
        # Abort if internal call
        if 'internal_request' in request.matchdict:
            return target(*args, **kwargs)
        
        if request.registry.settings.get('server.etag.enabled'):
            try:
                etag = generate_cache_key(request)
            except LookupError:
                log.debug('etag generation aborted, custom response detected')
                etag = None
            if etag:
                if etag in request.if_none_match:
                    log.debug('etag matched - aborting render - %s' % etag)
                    raise exception_response(304)
                else:
                    log.debug('etag set - %s' % etag)
                    request.response.etag = etag
        
        result = target(*args, **kwargs) # Execute the wrapped function
        
        return result
    return decorator(etag)
