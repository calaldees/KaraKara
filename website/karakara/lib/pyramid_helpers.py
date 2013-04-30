import datetime
import dateutil.parser

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
    if not value:
        return
    if return_type=='bool' or return_type==bool:
        value = asbool(value)
    if return_type=='int' or return_type==int:
        value = int(value)
    if return_type=='time' or return_type==datetime.time:
        value = dateutil.parser.parse(value).time()
    if return_type=='date' or return_type==datetime.date:
        value = dateutil.parser.parse(value).date()
    if return_type=='datetime' or return_type==datetime.datetime:
        value = dateutil.parser.parse(value)
    if return_type=='list' or return_type==list:
        value = [v.strip() for v in value.split(',') if v.strip()]
    return value


def request_from_args(args):
    # Extract request object from args
    for arg in args:
        if isinstance(arg, pyramid.request.Request):
            return arg
    raise Exception('no pyramid.request.Request in args')


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
