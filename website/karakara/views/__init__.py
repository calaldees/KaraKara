from decorator import decorator
from ..lib.pyramid_helpers import request_from_args, get_setting

id_count = 0

@decorator
def base(target, *args, **kwargs):
    """
    The base instructions to be executed for most calls
    """
    request = request_from_args(args)

    # The session id is abstracted from the framework. Keep a count/track id's as session values
    global id_count
    if 'id' not in request.session:
        request.session['id'] = id_count
        id_count += 1
    
    #request.session.flash('Hello World %d' % request.session['id'])
    
    result = target(*args, **kwargs)
    
    # Enable Pyramid GZip on all responses - NOTE! In a production this should be handled by nginx for performance!
    if get_setting('server.gzip', request, return_type=bool):
        request.response.encode_content(encoding='gzip', lazy=False)
    
    return result

# AllanC - need to look into Pyramids security model
def is_admin(request):
    return request.session['admin']

def set_admin(request):
    request.session['admin'] = True