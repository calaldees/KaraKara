from pyramid.view import view_config

from externals.lib.misc import convert_str

from . import action_ok, action_error, cache_manager, patch_cache_bucket_decorator

from ..model import DBSession, commit
from ..model.model_queue import QueueSetting

import logging
log = logging.getLogger(__name__)


SETTINGS_TYPE_MAPPING = {
    'karakara.system.user.readonly': 'bool',
    'karakara.event.end': 'datetime',

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
    'karakara.template.title': None,
    'karakara.template.menu.disable': None,

    # karakara.search.view.config = data/config/search_config.json
    'karakara.search.tag.silent_forced': 'list',
    'karakara.search.tag.silent_hidden': 'list',
    'karakara.search.template.button.list_tracks.threshold': 'int',
    'karakara.search.list.threshold': 'int',
    'karakara.search.list.alphabetical.threshold': 'int',
    'karakara.search.list.alphabetical.tags': 'list',
}


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
            queue_setting.key: convert_str(queue_setting.value, SETTINGS_TYPE_MAPPING.get(queue_setting.key))
            for queue_setting in DBSession.query(QueueSetting).filter(QueueSetting.queue_id == request.context.queue_id)
        }

        return {'settings': queue_settings}

    return action_ok(
        data=request.cache_bucket.get_or_create(get_queue_settings_dict)
        #data=get_queue_settings_dict()
    )


def queue_settings(request):
    """
    A wrapper for `queue_settings_view` to allow subrequests to access cached settings
    """
    return patch_cache_bucket_decorator(acquire_cache_bucket_func=acquire_cache_bucket_func)(queue_settings_view)(request)['data']['settings']
