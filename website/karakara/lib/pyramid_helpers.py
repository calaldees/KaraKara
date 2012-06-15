import pyramid.request
import pyramid.registry
from pyramid.settings import asbool
from pyramid.httpexceptions import exception_response

from decorator import decorator

import logging
log = logging.getLogger(__name__)


def get_setting(key, request=None, return_type=None):
    if request:
        value = request.registry.settings.get(key)
    else:
        value = pyramid.registry.global_registry.settings.get(key)
    if return_type=='bool' or return_type==bool:
        value = asbool(value)
    if return_type=='int' or return_type==int:
        value = int(value)
    return value

def request_from_args(args):
    # Extract request object from args
    request = None
    for arg in args:
        if isinstance(arg, pyramid.request.Request):
            request = arg
            break
    assert request
    return request



def etag(etag_render_func):
    def etag(f, *args, **kwargs):
        request = request_from_args(args)
        
        etag_enabled = get_setting('server.etag_enabled', request, return_type=bool)
        
        if (etag_enabled):
            if etag_render_func:
                etag = etag_render_func(request)
            else:
                etag = "%s %s" % (target.__name__, str(request.params) )
            if etag and etag in request.if_none_match:
                log.debug('etag matched - aborting render - %s' % etag)
                raise exception_response(304)
        
        result = f(*args, **kwargs) # Execute the wrapped function
        
        if (etag_enabled):
            log.debug('etag set - %s' % etag)
            result.etag = etag
            
        return result

    return decorator(etag)
