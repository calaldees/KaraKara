from pyramid.view import view_config

from . import action_ok, action_error, comunity_only

from ..model import DBSession, commit
from ..model.model_queue import QueueItem
from ..model.model_tracks import Track

from .queue_items import _queue_items_dict_with_track_dict


@view_config(
    context='karakara.traversal.ComunityQueueItemsContext',
)
@comunity_only
def community_settings_view(request):

    queue_dicts = _queue_items_dict_with_track_dict(
        DBSession.query(QueueItem).filter(QueueItem.queue_id==request.context.queue_id).order_by(QueueItem.queue_weight)
    )

    return action_ok(data={'queue': queue_dicts})
