from externals.lib.misc import decorator_combine

from externals.lib.pyramid.session_identity import overlay_session_identity
from externals.lib.pyramid import request_from_args, mark_external_request, method_delete_router, method_put_router
from externals.lib.pyramid.etag import etag, etag_decorator, _generate_cache_key_default
from externals.lib.pyramid.auto_format import auto_format_output, action_error
from externals.lib.pyramid.session_identity import overlay_session_identity

__all__ = [
    #'base','overlay_identity','auto_format_output','web',
    'etag','etag_decorator', #'etag_generate'
    'method_delete_router', 'method_put_router',
    'cache', 'cache_none',
]


#-------------------------------------------------------------------------------
# Global Variables
#-------------------------------------------------------------------------------

from dogpile.cache import make_region
from dogpile.cache.api import NO_VALUE as cache_none

cache = make_region().configure(
    'dogpile.cache.memory'
)



#web = decorator_combine(
#    auto_format_output,
#    overlay_session_identity(('id',)),
#    mark_external_request
#)

#-------------------------------------------------------------------------------
# State
#-------------------------------------------------------------------------------

# AllanC - need to look into Pyramids security model
def is_admin(request):
    return request.session.get('admin',False)  # request.session['admin']

#-------------------------------------------------------------------------------
# eTag
#-------------------------------------------------------------------------------
def generate_cache_key(request):
    if request.session.peek_flash():
        raise LookupError  # Response is not cacheable/indexable if there is a custom flash message
    return '-'.join([_generate_cache_key_default(request), str(is_admin(request))])
