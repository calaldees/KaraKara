from pyramid.view import view_config

from externals.lib.misc import convert_str

from . import action_ok, action_error, cache_manager, patch_cache_bucket_decorator, method_delete_router, method_put_router, is_admin

from ..model import DBSession, commit
from ..model.model_queue import QueueSetting

import logging
log = logging.getLogger(__name__)

# TODO: Translation strings for this file

REGISTRY_SETTINGS_PASSTHROUGH = {
    'karakara.websocket.port',
    'karakara.websocket.path',
}

SETTINGS_ADMIN_EXTRA_EXPOSE = {
    'karakara.private.password',
}

SETTINGS_TYPE_MAPPING = {
    'karakara.system.user.readonly': 'bool',
    'karakara.event.end': 'datetime',
    'karakara.event.start': 'datetime',

    'karakara.player.title': None,
    'karakara.player.video.preview_volume': 'float',
    'karakara.player.video.skip.seconds': 'int',
    'karakara.player.queue.update_time': 'timedelta',
    'karakara.player.help.timeout': 'int',

    'karakara.queue.group.split_markers': 'timedelta',
    'karakara.queue.track.padding': 'timedelta',

    'karakara.queue.add.limit': 'timedelta',
    'karakara.queue.add.limit.priority_token': 'timedelta',
    'karakara.queue.add.limit.priority_window': 'timedelta',
    'karakara.queue.add.duplicate.track_limit': 'int',
    'karakara.queue.add.duplicate.time_limit': 'timedelta',
    'karakara.queue.add.duplicate.performer_limit': 'int',
    'karakara.queue.add.valid_performer_names': 'list',

    'karakara.template.input.performer_name': None,
    'karakara.template.menu.disable': None,

    # karakara.search.view.config = data/config/search_config.json
    'karakara.search.tag.silent_forced': 'list',
    'karakara.search.tag.silent_hidden': 'list',
    'karakara.search.template.button.list_tracks.threshold': 'int',
    'karakara.search.list.threshold': 'int',
    'karakara.search.list.alphabetical.threshold': 'int',
    'karakara.search.list.alphabetical.tags': 'list',

    'karakara.print_tracks.fields': 'list',
    'karakara.print_tracks.short_id_length': 'int',
}


DEFAULT_SETTINGS = {
    'karakara.system.user.readonly': False,

    'karakara.player.title': 'KaraKara (dev player)',
    'karakara.player.video.preview_volume': 0.10,
    'karakara.player.video.skip.seconds': 20,
    'karakara.player.queue.update_time': '0:00:03',
    'karakara.player.help.timeout': 2,

    'karakara.queue.group.split_markers': '[0:15:00, 0:30:00]',
    'karakara.queue.track.padding': '0:00:60',

    'karakara.queue.add.limit': '0:40:00',
    'karakara.queue.add.limit.priority_token': '1:00:00',
    'karakara.queue.add.limit.priority_window': '0:02:30',
    'karakara.queue.add.duplicate.track_limit': 1,
    'karakara.queue.add.duplicate.time_limit': '0:30:00',
    'karakara.queue.add.duplicate.performer_limit': 1,
    'karakara.queue.add.valid_performer_names': '[]',

    'karakara.template.input.performer_name': '',
    'karakara.template.title': 'KaraKara (dev)',
    'karakara.template.menu.disable': '',

    #karakara.search.view.config = data/config/search_config.json
    'karakara.search.tag.silent_forced': '[]',
    'karakara.search.tag.silent_hidden': '[todo, delete, broken]',
    'karakara.search.template.button.list_tracks.threshold': 100,
    'karakara.search.list.threshold': 25,
    'karakara.search.list.alphabetical.threshold': 90,
    'karakara.search.list.alphabetical.tags': '[from, artist]',

    'karakara.print_tracks.fields': '[category, from, use, title, artist, vocaltrack, length]',
    'karakara.print_tracks.short_id_length': 4,

    'karakara.event.end': '',
    'karakara.event.start': '',
}
DEFAULT_SETTINGS = {
    k: convert_str(v, SETTINGS_TYPE_MAPPING.get(k))
    for k, v in DEFAULT_SETTINGS.items()
}
SETTING_IDENTIFIER = 'karakara'
SETTING_IDENTIFIER_PRIVATE = f'{SETTING_IDENTIFIER}.private'  # Possibly replace this with a list of allowed private keys


def acquire_cache_bucket_func(request):
    return cache_manager.get(f'queue-settings-{request.context.queue_id}')


@view_config(
    context='karakara.traversal.QueueSettingsContext',
    request_method='GET',
    acquire_cache_bucket_func=acquire_cache_bucket_func,
)
def queue_settings_view(request):

    def get_queue_settings_dict():
        log.debug(f'cache gen - queue settings {request.cache_bucket.version}')

        queue_settings = {
            **DEFAULT_SETTINGS,
            **{
                k: request.registry.settings[k]
                for k in REGISTRY_SETTINGS_PASSTHROUGH
            },
            **{
                queue_setting.key: convert_str(queue_setting.value, SETTINGS_TYPE_MAPPING.get(queue_setting.key))
                for queue_setting in DBSession.query(QueueSetting).filter(QueueSetting.queue_id == request.context.queue_id)
            },
        }
        queue_settings = {
            k: v
            for k, v in queue_settings.items()
            if not k.startswith(SETTING_IDENTIFIER_PRIVATE)
        }
        return {'settings': queue_settings}

    return action_ok(data=request.cache_bucket.get_or_create(get_queue_settings_dict))


@view_config(
    context='karakara.traversal.QueueSettingsContext',
    custom_predicates=(method_put_router, ),
    acquire_cache_bucket_func=acquire_cache_bucket_func,
)
def queue_settings_view_put(request):
    if request.registry.settings.get('karakara.server.mode') != 'test' and not is_admin(request):
        raise action_error(message='Settings modification for non admin users forbidden', code=403)

    queue_setting_objs = {
        queue_setting_obj.key: queue_setting_obj
        for queue_setting_obj in DBSession.query(QueueSetting).filter(QueueSetting.queue_id == request.context.queue_id)
    }

    def get_or_create_queue_settings_obj(key):
        if key in queue_setting_objs:
            return queue_setting_objs[key]
        else:
            queue_setting_obj = QueueSetting()
            queue_setting_obj.queue_id = request.context.queue_id
            queue_setting_obj.key = key
            DBSession.add(queue_setting_obj)
            queue_setting_objs[key] = queue_setting_obj
            return queue_setting_obj

    def is_valid(key, value):
        try:
            convert_str(value, SETTINGS_TYPE_MAPPING.get(key))
            return True
        except AssertionError:
            return False

    error_messages = []
    for key, value in request.params.items():
        if (
            (not key.startswith(SETTING_IDENTIFIER)) or  # Drop random other fields (like 'format' or 'method')
            (key in REGISTRY_SETTINGS_PASSTHROUGH) or  # These are not editable settings for the queue, they are global and cannot be set
            (not value and key in SETTINGS_ADMIN_EXTRA_EXPOSE)  # Ignore extra admin keys if they are empty (this prevents stomping on 'password'. This probably needs more thought
        ):
            continue
        if is_valid(key, value):
            get_or_create_queue_settings_obj(key).value = value
        else:
            error_messages.append(f'{key}:{value} is not valid')
    if error_messages:
        raise action_error(messages=error_messages, code=400)

    request.cache_bucket.invalidate()
    request.log_event(method='update', admin=is_admin(request))
    request.send_websocket_message('settings')  # Ensure that the player interface is notified of an update

    return action_ok(message='queue_settings updated')
