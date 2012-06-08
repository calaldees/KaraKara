from decorator import decorator
from ..lib.pyramid_helpers import request_from_args

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
    return result

# AllanC - need to look into Pyramids security model
def is_admin(request):
    return request.session['admin']

def set_admin(request):
    request.session['admin'] = True