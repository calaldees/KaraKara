
from datetime import timedelta
from decorator import decorator

from dogpile.cache.api import NO_VALUE as cache_none  # bit of contamination here - cache is backed by dogpile

from calaldees.decorator import decorator_combine

from calaldees.pyramid_helpers import request_from_args, mark_external_request, gzip
from calaldees.pyramid_helpers.etag import etag, etag_decorator, _generate_cache_key_default
from calaldees.pyramid_helpers.auto_format2 import action_ok, action_error


import logging
log = logging.getLogger(__name__)


#from .message import overlay_messages

__all__ = [
    'web', 'action_ok', 'action_error',  #'auto_format_output'
    'etag','etag_decorator', #'etag_generate'
    'cache_none',
    #'max_age',
]



web = decorator_combine(
    #gzip,
    #auto_format_output,
    #overlay_messages(),
    mark_external_request
)


#-------------------------------------------------------------------------------
# State
#-------------------------------------------------------------------------------

# AllanC - need to look into Pyramids security model
def is_admin(request):
    return request.session_identity['admin']

def is_community(request):
    return request.session.get('user',{}).get('approved', False)

@decorator
def admin_only(target, *args, **kwargs):
    """
    Decorator to restrict view callable to admin users only
    todo - use pyramid's security framework
    """
    request = request_from_args(args)
    if not is_admin(request):
        raise action_error(message='Administrators only', code=403)

    return target(*args, **kwargs)

@decorator
def community_only(target, *args, **kwargs):
    """
    Decorator to restrict view callable to approved community users only
    todo - use pyramid's security framework
    """
    request = request_from_args(args)
    if not is_community(request):
        raise action_error(message='Approved community users only', code=403)

    return target(*args, **kwargs)


@decorator
def modification_action(target, *args, **kwargs):
    """
    Check readonly mode and abort non admins
    """
    request = request_from_args(args)
    if not is_admin(request) and request.queue.settings.get('karakara.system.user.readonly'):
        raise action_error(message='normal users are in readonly mode', code=403)

    return target(*args, **kwargs)


#-------------------------------------------------------------------------------
# eTag
#-------------------------------------------------------------------------------
def generate_cache_key(request):
    if request.session.peek_flash():
        raise LookupError  # Response is not cacheable/indexable if there is a custom flash message
    return '-'.join([_generate_cache_key_default(request), str(is_admin(request))])
