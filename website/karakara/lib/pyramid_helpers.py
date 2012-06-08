import pyramid.request
import pyramid.registry
from pyramid.settings import asbool


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
