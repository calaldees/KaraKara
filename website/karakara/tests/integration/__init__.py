import functools

import logging
log = logging.getLogger(__name__)


def get_settings(app):
    return app.get('/settings.json').json['data']['settings']


class temporary_setting:
    def __init__(self, app, key, value):
        self.app = app
        self.key = key
        self.value = value

    def __enter__(self):
        self.original_value = get_settings(self.app)[self.key]
        self.app.put('/settings.json', {self.key: self.value})
        log.debug('Temporay setting {0}:{1} -> {2}'.format(self.key, self.original_value, self.value))
        return None
    
    def __exit__(self, type, value, traceback):
        self.app.put('/settings.json', {self.key: self.original_value})
        log.debug('Temporay setting {0} reverted to {1}'.format(self.key, self.original_value))


def apply_setting(method=None, key='', value=''):
    """
    GAH!! this is broken .. wtf!?
    
    Decorator to set setting for tests and revert them post test
    first arg must be 'app'
    """
    if method is None:
        return functools.partial(apply_setting, key=key, value=value)
    @functools.wraps(method)
    def f(*args, **kwargs):
        with temporary_setting(kwargs['app'], key, value):
            return_value = method(*args, **kwargs)
        return return_value
    return f
