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
        def empty_list_hack(value):
            # Hack to fix reverting to empty list
            if value == []:  
                return '[]'
            return value
        self.app.put('/settings.json', {self.key: empty_list_hack(self.original_value)})
        log.debug('Temporay setting {0} reverted to {1}'.format(self.key, self.original_value))
        # TODO: Research needed; Consider correct handling of exceptions as they propergate up
        # Next line can be removed for perfomance once this test method is verifyed as working under all conditions
        #current_setting = get_settings(self.app)[self.key]
        #assert current_setting == self.original_value, 'The setting {0} should have been reverted to its original state of {1}. It is still {2}'.format(self.key, self.original_value, current_setting)


class admin_rights:
    def __init__(self, app):
        self.app = app

    def __enter__(self):
        return None  # TODO: ReImplement this properly
        admin_state = self.app.get('/admin.json').json['identity']['admin']
        self.original_value = not admin_state
        if admin_state:
            log.debug('Set admin mode')
        else:
            # We altered the admin state inadvertenty from enabled to disabled, ensure it's enabled
            assert self.app.get('/admin.json').json['identity']['admin']
        return None

    def __exit__(self, type, value, traceback):
        return None  # TODO: ReImplement this properly
        # If admin mode was not enabled at the beggining, ensure it is revolked again
        if not self.original_value:
            assert not self.app.get('/admin.json').json['identity']['admin']
            log.debug('Revolked admin right')


def with_setting(method=None, key='', value=''):
    """
    Decorator to set setting for tests and revert them post test
    first arg must be 'app'
    """
    if method is None:
        return functools.partial(with_setting, key=key, value=value)
    @functools.wraps(method)
    def f(*args, **kwargs):
        with temporary_setting(kwargs['app'], key, value):
            return_value = method(*args, **kwargs)
        return return_value
    return f
