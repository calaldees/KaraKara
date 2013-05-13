from decorator import decorator
from ..lib.misc            import random_string
from ..lib.pyramid_helpers import request_from_args, etag, _etag_render_func_default
from ..lib.auto_format     import auto_format_output, action_error

__all__ = [
    'base','overlay_identity','auto_format_output','web','etag', 'etag_generate'
    'method_delete_router', 'method_put_router',
]


#-------------------------------------------------------------------------------
# Global Variables
#-------------------------------------------------------------------------------




#-------------------------------------------------------------------------------
# Base - executed on all calls
#-------------------------------------------------------------------------------
@decorator
def base(target, *args, **kwargs):
    """
    The base instructions to be executed for most calls
    """
    request = request_from_args(args)
    
    # Abort if internal call
    if 'internal_request' in request.matchdict:
        return target(*args, **kwargs)

    # The session id is abstracted from the framework. Keep a count/track id's as session values
    if 'id' not in request.session:
        request.session['id'] = random_string()
    
    #request.session.flash('Hello World %d' % request.session['id'])
    
    result = target(*args, **kwargs)
    
    # Enable Pyramid GZip on all responses - NOTE! In a production this should be handled by nginx for performance!
    if request.registry.settings.get('server.gzip'):
        request.response.encode_content(encoding='gzip', lazy=False)
    
    return result

#-------------------------------------------------------------------------------
# Overlay Identity
#-------------------------------------------------------------------------------
@decorator
def overlay_identity(target, *args, **kwargs):
    """
    Decorator to post process an action_ok dict and append the current users details to the return
    This ensure that our local templates and external client's have the same data to work with when rendering
    """
    request = request_from_args(args)
    
    # Abort if internal call
    if 'internal_request' in request.matchdict:
        return target(*args, **kwargs)
    
    def overlay_identity_onto(target_dict):
        identity_dict = {}
        for key in ['id','admin','faves']:
            identity_dict[key] = request.session.get(key,None)
        target_dict['identity'] = identity_dict

    try:
        result = target(*args, **kwargs)
    except action_error as ae:
        # overlay identity onto action_errors
        overlay_identity_onto(ae.d)
        raise ae
    
    # Overlay a new dict called identity onto each request
    if isinstance(result, dict):
        overlay_identity_onto(result)
    
    return result

@decorator
def mark_external_request(target, *args, **kwargs):
    """
    All the decorators fire on almost every call.
    If we have 'internal_request' in our request, then most of the decorators should short circit and abort.
    this enables us to use internal API calls.
    decorators that may still fire for internal calls are things like cache lookup
    This should be the absolute closest decorator to the actual method call as possible
    """
    request_from_args(args).matchdict['internal_request'] = True
    return target(*args, **kwargs)


#-------------------------------------------------------------------------------
# Web - the decorators merged
#-------------------------------------------------------------------------------
# Reference - http://stackoverflow.com/questions/2182858/how-can-i-pack-serveral-decorators-into-one

def chained(*dec_funs):
    def _inner_chain(f):
        for dec in reversed(dec_funs):
            f = dec(f)
        return f
    return _inner_chain

web  = chained(base, auto_format_output, overlay_identity, mark_external_request)


#-------------------------------------------------------------------------------
# Predicates
#-------------------------------------------------------------------------------

def method_delete_router(info, request):
    if request.method == 'DELETE' or request.params.get('method','GET').upper() == 'DELETE':
        return True

def method_put_router(info, request):
    if request.method == 'PUT' or request.params.get('method','GET').upper() == 'PUT':
        return True


#-------------------------------------------------------------------------------
# State
#-------------------------------------------------------------------------------

# AllanC - need to look into Pyramids security model
def is_admin(request):
    return request.session.get('admin',False)  # request.session['admin']

#-------------------------------------------------------------------------------
# eTag
#-------------------------------------------------------------------------------
def etag_generate(request):
    return '-'.join([_etag_render_func_default(request), str(is_admin(request)), str(request.session.peek_flash())])
