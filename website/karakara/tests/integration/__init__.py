import functools

from calaldees.string_convert import _string_list_format_hack

import logging
log = logging.getLogger(__name__)


def get_settings(app, queue):
    return app.get(f'/queue/{queue}/settings.json').json['data']['settings']


class temporary_settings:
    def __init__(self, app, queue, settings_dict):
        self.app = app
        self.queue = queue
        self.settings_dict = settings_dict
        self.settings_url = f'/queue/{queue}/settings.json'

    @property
    def settings(self):
        return get_settings(self.app, self.queue)

    def __enter__(self):
        settings = self.settings
        self.settings_original_values = {k: settings[k] for k, v in self.settings_dict.items()}
        self.app.put(self.settings_url, self.settings_dict)
        log.debug(f'Temporay setting {self.settings_original_values} -> {self.settings_dict}')
        return None

    def __exit__(self, type, value, traceback):
        self.app.put(self.settings_url, {k: _string_list_format_hack(v) for k, v in self.settings_original_values.items()})
        log.debug(f'Temporay setting {self.settings_dict} reverted to {self.settings_original_values}')
        # TODO: Research needed; Consider correct handling of exceptions as they propergate up
        # Next line can be removed for perfomance once this test method is verifyed as working under all conditions
        settings = self.settings
        settings = {k: settings[k] for k, v in self.settings_dict.items()}
        assert settings == self.settings_original_values, f'The settings {settings} should have been reverted to its original state of {self.settings_original_values}.'


class admin_rights:
    ADMIN_PASSWORD = 'qtest'

    def __init__(self, app, queue):
        self.app = app
        self.queue_url = f'/queue/{queue}'

    @property
    def is_admin(self):
        return bool(self.app.get(f'{self.queue_url}?format=json').json['identity']['admin'])
    @is_admin.setter
    def is_admin(self, value):
        password = self.ADMIN_PASSWORD if value else ''
        self.app.get(f'{self.queue_url}/admin.json?password={password}').json['identity']['admin']  # TODO: expect auto assertion errors stuff
        assert self.is_admin == value

    def __enter__(self):
        self.original_value = self.is_admin
        self.is_admin = True
        return None

    def __exit__(self, type, value, traceback):
        # If admin mode was not enabled at the beggining, ensure it is revolked again
        if not self.original_value:
            self.is_admin = self.original_value
            log.debug('Reverted admin rights')


def with_settings(method=None, settings={}):
    """
    Decorator to set setting for tests and revert them post test
    first arg must be 'app'
    """
    if method is None:
        return functools.partial(with_settings, settings=settings)
    @functools.wraps(method)
    def f(*args, **kwargs):
        with temporary_settings(kwargs['app'], kwargs['queue'], settings):
            return_value = method(*args, **kwargs)
        return return_value
    return f
