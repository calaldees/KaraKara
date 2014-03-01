from decorator import decorator

from externals.lib.misc import decorator_combine

from externals.lib.pyramid import request_from_args, mark_external_request, method_delete_router, method_put_router, max_age, gzip
from externals.lib.pyramid.etag import etag, etag_decorator, _generate_cache_key_default
from externals.lib.pyramid.auto_format import auto_format_output, action_ok, action_error
from externals.lib.pyramid.session_identity import overlay_session_identity

__all__ = [
    'web', 'action_ok', 'action_error',  #'auto_format_output'
    'etag','etag_decorator', #'etag_generate'
    'method_delete_router', 'method_put_router',
    'cache', 'cache_none',
    'max_age',
]


#-------------------------------------------------------------------------------
# Global Variables
#-------------------------------------------------------------------------------

from dogpile.cache import make_region
from dogpile.cache.api import NO_VALUE as cache_none

cache = make_region().configure(
    'dogpile.cache.memory'
)


web = decorator_combine(
    gzip,
    auto_format_output,
    overlay_session_identity(('id','admin','faves')),
    mark_external_request
)


#-------------------------------------------------------------------------------
# State
#-------------------------------------------------------------------------------

# AllanC - need to look into Pyramids security model
def is_admin(request):
    return request.session.get('admin',False)  # request.session['admin']


@decorator
def admin_only(target, *args, **kwargs):
    """
    Decorator to restrict view callable to admin users only
    """
    request = request_from_args(args)
    if not is_admin(request):
        raise action_error(message='Administrators only', code=403)

    return target(*args, **kwargs)


@decorator
def modification_action(target, *args, **kwargs):
    """
    Check readonly mode and abort non admins
    """
    request = request_from_args(args)
    if not is_admin(request) and request.registry.settings.get('karakara.system.user.readonly'):
        raise action_error(message='normal users are in readonly mode', code=403)

    return target(*args, **kwargs)


#-------------------------------------------------------------------------------
# eTag
#-------------------------------------------------------------------------------
def generate_cache_key(request):
    if request.session.peek_flash():
        raise LookupError  # Response is not cacheable/indexable if there is a custom flash message
    return '-'.join([_generate_cache_key_default(request), str(is_admin(request))])
