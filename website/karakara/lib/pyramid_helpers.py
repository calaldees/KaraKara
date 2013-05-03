import datetime
import dateutil.parser

import pyramid.request
import pyramid.registry
from pyramid.httpexceptions import exception_response

from decorator import decorator


import logging
log = logging.getLogger(__name__)


#def get_setting(key, request=None, return_type=None):
#    """
#    DEPRICATED
#    """
#    if request:
#        value = request.registry.settings.get(key)
#    else:
#        value = pyramid.registry.global_registry.settings.get(key)
#    return convert_str(value, return_type)
    


def request_from_args(args):
    # Extract request object from args
    for arg in args:
        if isinstance(arg, pyramid.request.Request):
            return arg
    raise Exception('no pyramid.request.Request in args')


def etag(etag_render_func):
    def etag(f, *args, **kwargs):
        request = request_from_args(args)
        
        etag_enabled = request.registry.settings.get('server.etag_enabled')
        
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
