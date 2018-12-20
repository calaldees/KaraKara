
from datetime import timedelta
from decorator import decorator

from calaldees.date_tools import normalize_datetime
from calaldees.decorator import decorator_combine

from calaldees.pyramid_helpers import request_from_args, mark_external_request, method_delete_router, method_put_router, gzip
from calaldees.pyramid_helpers.etag import etag, etag_decorator, _generate_cache_key_default
from calaldees.pyramid_helpers.cache_manager import CacheManager, CacheFunctionWrapper, patch_cache_bucket_decorator
from calaldees.pyramid_helpers.auto_format2 import action_ok, action_error

from karakara.model import commit


import logging
log = logging.getLogger(__name__)


#from .message import overlay_messages

__all__ = [
    'web', 'action_ok', 'action_error',  #'auto_format_output'
    'etag','etag_decorator', #'etag_generate'
    'method_delete_router', 'method_put_router',
    'cache_manager', 'cache_none', 'patch_cache_bucket_decorator',
    #'max_age',
]


#-------------------------------------------------------------------------------
# Global Variables
#-------------------------------------------------------------------------------

import dogpile.cache
from dogpile.cache.api import NO_VALUE as cache_none


cache_store = dogpile.cache.make_region().configure(
    backend='dogpile.cache.memory',
    expiration_time=timedelta(hours=1),
)

cache = cache_store  # TODO: remove passing alias DEPRICATED!


#-------------------------------------------------------------------------------
# Cache Management
#-------------------------------------------------------------------------------


def _cache_key_etag_expire(request):
    cache_bust = request.registry.settings.get('server.etag.cache_buster', ''),
    etag_expire = normalize_datetime(accuracy=request.registry.settings.get('server.etag.expire')).ctime(),
    return f'{cache_bust}-{etag_expire}'


def _cache_key_identity_admin(request):
    if request.session.peek_flash():
        raise LookupError  # Response is not cacheable/indexable if there is a custom flash message
    return is_admin(request)


cache_manager = CacheManager(
    cache_store=cache_store,
    default_cache_key_generators=(
        CacheFunctionWrapper(_cache_key_etag_expire, ('request', )),
        CacheFunctionWrapper(_cache_key_identity_admin, ('request', )),
    ),
    default_invalidate_callbacks=(
        CacheFunctionWrapper(commit, ()),
    )
)


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
    return request.session.get('admin', False)  # request.session['admin']

def is_comunity(request):
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
def comunity_only(target, *args, **kwargs):
    """
    Decorator to restrict view callable to approved comunity users only
    todo - use pyramid's security framework
    """
    request = request_from_args(args)
    if not is_comunity(request):
        raise action_error(message='Approved comunity users only', code=403)

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
