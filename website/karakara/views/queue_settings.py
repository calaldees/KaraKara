"""
Settings to migrate from registry

karakara.system.user.readonly = False -> bool

karakara.event.end                       = -> datetime

karakara.player.title                          = KaraKara (dev player)
karakara.player.video.preview_volume           =  0.10   -> float
karakara.player.video.skip.seconds             = 20      -> int
karakara.player.queue.update_time              = 0:00:03 -> timedelta
karakara.player.help.timeout                   =  2      -> int

karakara.queue.group.split_markers = [0:10:00, 0:20:00] -> timedelta
karakara.queue.track.padding       = 0:00:60 -> timedelta

karakara.queue.add.limit                     = 0:10:00 -> timedelta
karakara.queue.add.limit.priority_token      = 0:00:00 -> timedelta
karakara.queue.add.limit.priority_window     = 0:01:00 -> timedelta
karakara.queue.add.duplicate.track_limit     = 2       -> int
karakara.queue.add.duplicate.time_limit      = 1:00:00 -> timedelta
karakara.queue.add.duplicate.performer_limit = 1       -> int
karakara.queue.add.valid_performer_names = [] -> list

karakara.template.input.performer_name = 
karakara.template.title                = KaraKara (dev)
karakara.template.menu.disable =

karakara.search.view.config = data/config/search_config.json
karakara.search.tag.silent_forced = []
karakara.search.tag.silent_hidden = []
karakara.search.template.button.list_tracks.threshold = 100 -> int
karakara.search.list.threshold = 25 -> int
karakara.search.list.alphabetical.threshold = 90 -> int
karakara.search.list.alphabetical.tags = [from, artist]

"""
from pyramid.view import view_config

from . import action_ok, action_error, cache_manager, patch_cache_bucket_decorator

from ..model import DBSession, commit
from ..model.model_queue import QueueSetting

import logging
log = logging.getLogger(__name__)


def acquire_cache_bucket_func(request):
    return cache_manager.get(f'queue-settings-{request.context.queue_id}')


@view_config(
    context='karakara.traversal.QueueSettingsContext',
    request_method='GET',
    acquire_cache_bucket_func=acquire_cache_bucket_func,
)
@patch_cache_bucket_decorator(acquire_cache_bucket_func=acquire_cache_bucket_func)
def queue_settings_view(request):

    def get_queue_settings_dict():
        log.debug(f'cache gen - queue settings {request.cache_bucket.version}')

        queue_settings = {
            queue_setting.key: queue_setting.value
            for queue_setting in DBSession.query(QueueSetting).filter(QueueSetting.queue_id == request.context.queue_id)
        }

        return {'settings': queue_settings}

    import pdb ; pdb.set_trace()
    return action_ok(
        data=request.cache_bucket.get_or_create(get_queue_settings_dict)
        #data=get_queue_settings_dict()
    )
