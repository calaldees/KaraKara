from pyramid.view import view_config

from . import action_ok, community_only

from ..model import DBSession
from ..model.model_queue import QueueItem

from .queue_items import _queue_items_dict_with_track_dict


@view_config(
    context='karakara.traversal.CommunityQueueItemsContext',
)
@community_only
def community_settings_view(request):
    time_padding = request.queue.settings.get('karakara.queue.track.padding')
    queue_dicts = _queue_items_dict_with_track_dict(
        DBSession.query(QueueItem).filter(QueueItem.queue_id==request.context.queue_id).order_by(QueueItem.queue_weight),
        time_padding
    )
    return action_ok(data={'queue': queue_dicts})
