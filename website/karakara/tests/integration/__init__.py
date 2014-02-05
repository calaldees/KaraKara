import functools

import logging
log = logging.getLogger(__name__)


def setting(method=None, key='', value=''):
    """
    Decorator to set setting for tests and revert them post test
    first arg must be 'app'
    """
    if method is None:
        return functools.partial(setting, key=key, value=value)
    @functools.wraps(method)
    def f(*args, **kwargs):
        app = kwargs['app']
        
        original_value = app.get('/settings.json').json['data']['settings'][key]
        app.put('/settings.json', {key:value})
        log.debug('Temporay setting {0}:{1} -> {2}'.format(key, original_value, value))
        
        return_value = method(*args, **kwargs)
        
        app.put('/settings.json', {key:original_value})
        log.debug('Temporay setting {0} reverted to {1}'.format(key, original_value))
        
        return return_value
    return f
