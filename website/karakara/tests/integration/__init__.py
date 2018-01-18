import functools

import logging
log = logging.getLogger(__name__)


def get_settings(app, queue):
    return app.get(f'/queue/{queue}/settings.json').json['data']['settings']


class temporary_setting:
    def __init__(self, app, queue, key, value):
        self.app = app
        self.queue = queue
        self.key = key
        self.value = value
        self.settings_url = f'/queue/{self.queue}/settings.json'

    @property
    def settings(self):
        return get_settings(self.app, self.queue)

    def __enter__(self):
        self.original_value = self.settings[self.key]
        self.app.put(self.settings_url, {self.key: self.value})
        log.debug(f'Temporay setting {self.key}:{self.original_value} -> {self.value}')
        return None

    def __exit__(self, type, value, traceback):
        #def empty_list_hack(value):
        #    # Hack to fix reverting to empty list
        #    if value == []:
        #        return '[]'
        #    return value
        self.app.put(self.settings_url, {self.key: self.original_value})  # empty_list_hack(original_value)
        log.debug(f'Temporay setting {self.key} reverted to {self.original_value}')
        # TODO: Research needed; Consider correct handling of exceptions as they propergate up
        # Next line can be removed for perfomance once this test method is verifyed as working under all conditions
        current_setting = self.settings[self.key]
        assert current_setting == self.original_value, f'The setting {self.key} should have been reverted to its original state of {self.original_value}. It is still {current_setting}.'


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
        with temporary_setting(kwargs['app'], kwargs['queue'], key, value):
            return_value = method(*args, **kwargs)
        return return_value
    return f
