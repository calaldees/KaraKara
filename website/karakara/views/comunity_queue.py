from pyramid.view import view_config

from . import action_ok, action_error, comunity_only, method_delete_router


from ..model import DBSession, commit
from ..model.model_queue import Queue
from ..model.actions import delete_queue


@view_config(
    context='karakara.traversal.ComunityQueueContext',
    request_method='GET',
)
@comunity_only
def comunity_queue_view(request):
    return action_ok(data={'queues': tuple(queue.to_dict() for queue in DBSession.query(Queue))})


@view_config(
    context='karakara.traversal.ComunityQueueContext',
    request_method='POST',
)
@comunity_only
def comunity_queue_add(request):
    queue = Queue()
    for key, value in request.params.items():
        if hasattr(queue, key):
            setattr(queue, key, value)
    DBSession.add(queue)
    return action_ok(code=201)


@view_config(
    context='karakara.traversal.ComunityQueueContext',
    custom_predicates=(
        method_delete_router,
        lambda info, request: request.params.get('queue.id')
    )
)
@comunity_only
def queue_item_del(request):
    delete_queue(request.params.get('queue.id'))
    return action_ok()
