import datetime
from functools import partial

from sqlalchemy.orm import joinedload, defer  # , joinedload_all
from sqlalchemy.orm.exc import NoResultFound

from pyramid.view import view_config

from externals.lib.misc import now, subdict

from . import web, action_ok, action_error, etag_decorator, cache_manager, method_delete_router, method_put_router, is_admin, modification_action, admin_only

from ..model import DBSession, commit
from ..model.model_queue import QueueItem
from ..model.model_tracks import Track
from ..model.model_priority_token import PriorityToken
from ..model.actions import get_track

from ..templates.helpers import track_title

from ..model_logic import QUEUE_DUPLICATE, TOKEN_ISSUE_ERROR

#from .track import invalidate_track

import logging
log = logging.getLogger(__name__)



def socket_update_queue_items_event(request):
    # TODO: This needs to incorporate the alert for the specific queue_id
    request.socket_manager.recv('queue_updated'.encode('utf-8'))
#cache_manager.get('queue_items').register_invalidate_callback(socket_update_queue_items_event, ('request', ))

def acquire_cache_bucket_func(request):
    return cache_manager.get(f'queue-{request.context.queue_id}')

def invalidate_cache(request, track_id):
    request.cache_bucket.invalidate(request=request)  # same as acquire_cache_bucket_func(request)
    cache_manager.get(f'queue-{request.context.queue_id}-track-{track_id}').invalidate(request=request)


#-------------------------------------------------------------------------------
# Queue
#-------------------------------------------------------------------------------

#@view_config(route_name='queue', request_method='GET')
@view_config(
    context='karakara.traversal.QueueItemsContext',
    request_method='GET',
    acquire_cache_bucket_func=acquire_cache_bucket_func,
)
def queue_items_view(request):
    """
    view current queue
    """
    def get_queue_dict():
        log.debug('cache gen - queue {0}'.format(request.cache_bucket.version))

        # Get queue order
        queue_dicts = DBSession.query(QueueItem).filter(QueueItem.status=='pending').order_by(QueueItem.queue_weight)
        queue_dicts = [queue_item.to_dict('full') for queue_item in queue_dicts]

        # Fetch all tracks with id's in the queue
        trackids = [queue_item['track_id'] for queue_item in queue_dicts]
        tracks = {}
        if trackids:
            tracks = DBSession.query(Track).\
                                filter(Track.id.in_(trackids)).\
                                options(\
                                    joinedload(Track.tags),\
                                    joinedload(Track.attachments),\
                                    joinedload('tags.parent'),\
                                    #defer(Track.lyrics),\
                                )
            tracks = {track['id']:track for track in [track.to_dict('full', exclude_fields='lyrics') for track in tracks]}

        # HACK
        # AllanC - Hack to overlay title on API return.
        # This technically cant be part of the model because the title rendering in 'helpers' uses the dict version of a track object rather than the DB object
        # This is half the best place for it. We want the model to be as clean as possible
        # But we need the 'title' field to be consistant for all API returns for tracks ... more consideration needed
        #
        # Solution: Setup SQLAlchemy event to render the title before commiting a track to the DB - like a DB trigger by handled Python size for cross db compatibility
        #           Stub created in model_track.py
        #           This is to be removed ...
        for track in tracks.values():
            track['title'] = track_title(track['tags'])

        # Attach track to queue_item
        for queue_item in queue_dicts:
            queue_item['track'] = tracks.get(queue_item['track_id'])

        # Calculate estimated track time
        # Overlay 'total_duration' on all tracks
        # It takes time for performers to change, so each track add a padding time
        #  +
        # Calculate the index to split the queue list
        #  - non admin users do not see the whole queue in order.
        #  - after a specifyed time threshold, the quque order is obscured
        #  - it is expected that consumers of this api return will obscure the
        #    order passed the specifyed 'split_index'
        split_markers = list(request.queue.settings.get('karakara.queue.group.split_markers'))
        time_padding = request.queue.settings.get('karakara.queue.track.padding')
        split_indexs = []
        total_duration = datetime.timedelta(seconds=0)
        for index, queue_item in enumerate(queue_dicts):
            if not queue_item['track']:
                continue
            queue_item['total_duration'] = total_duration
            total_duration += datetime.timedelta(seconds=queue_item['track']['duration']) + time_padding
            if split_markers and total_duration > split_markers[0]:
                split_indexs.append(index + 1)
                del split_markers[0]

        return {'queue': queue_dicts, 'queue_split_indexs': split_indexs}

    return action_ok(
        data=request.cache_bucket.get_or_create(get_queue_dict)
        #data=get_queue_dict()
    )


#@view_config(route_name='queue', request_method='POST')
@view_config(
    context='karakara.traversal.QueueItemsContext',
    request_method='POST',
    acquire_cache_bucket_func=acquire_cache_bucket_func,
)
@modification_action
def queue_item_add(request):
    """
    Add items to end of queue
    """
    _ = request.translate
    _log_event = partial(request.log_event, method='add')

    # Validation
    for field in ['track_id', 'performer_name']:
        if not request.params.get(field):
            raise action_error(message='no {0}'.format(field), code=400)
    track_id = request.params.get('track_id')
    try:
        track = DBSession.query(Track).get(track_id)
        assert track
    except AssertionError:
        raise action_error(message=_('view.queue.add.error.track_id ${track_id}', mapping={'track_id': track_id}), code=400)

    # If not admin, check additional restrictions
    if not is_admin(request):

        performer_name = request.params.get('performer_name').strip()  # TODO: It would be good to ensure this value is writen to the db. However we cant modify the request.param dict directly. See creation of queueitem below

        # Valid performer name
        valid_performer_names = request.queue.settings.get('karakara.queue.add.valid_performer_names')
        if valid_performer_names and performer_name.lower() not in map(lambda name: name.lower(), valid_performer_names):
            message = _('view.queue.add.invalid_performer_name ${performer_name}', mapping=dict(
                performer_name=performer_name
            ))
            raise action_error(message, code=400)

        # Duplucate performer resrictions
        queue_item_performed_tracks = request.queue.for_performer(request.params.get('performer_name'))
        if queue_item_performed_tracks['performer_status'] == QUEUE_DUPLICATE.THRESHOLD:
            try:
                latest_track_title = get_track(queue_item_performed_tracks['queue_items'][0].track_id).title
            except Exception:
                latest_track_title = ''
            message = _('view.queue.add.dupicate_performer_limit ${performer_name} ${estimated_next_add_time} ${track_count} ${latest_queue_item_title}', mapping=dict(
                performer_name=performer_name,
                latest_queue_item_title=latest_track_title,
                **subdict(queue_item_performed_tracks, {
                    'estimated_next_add_time',
                    'track_count',
                })
            ))
            _log_event(status='reject', reason='dupicate.performer', message=message)
            raise action_error(message=message, code=400)

        # Duplicate Addition Restrictions
        queue_item_tracks_queued = request.queue.for_track(track.id)
        if queue_item_tracks_queued['track_status'] == QUEUE_DUPLICATE.THRESHOLD:
            message = _('view.queue.add.dupicate_track_limit ${track_id} ${estimated_next_add_time} ${track_count}', mapping=dict(
                track_id=track.id,
                **subdict(queue_item_performed_tracks, {
                    'estimated_next_add_time',
                    'track_count',
                })
            ))
            _log_event(status='reject', reason='duplicate.track', message=message)
            raise action_error(message=message, code=400)

        # Event end time
        event_end = request.queue.settings.get('karakara.event.end')
        if event_end and now() + request.queue.duration > event_end:
            log.debug('event end restricted')
            _log_event(status='reject', reason='event_end')
            raise action_error(message=_('view.queue.add.event_end ${event_end}', mapping={'event_end': event_end}), code=400)

        # Queue time limit
        queue_limit = request.queue.settings.get('karakara.queue.add.limit')
        if queue_limit and request.queue.duration > queue_limit:
            # If no device priority token - issue token and abort
            # else consume the token and proceed with addition
            if not _logic.consume_priority_token(request, DBSession):
                # Issue a priority token
                priority_token = _logic.issue_priority_token(request, DBSession)
                if isinstance(priority_token, PriorityToken):
                    _log_event(status='reject', reason='token.issued')
                    raise action_error(message=_('view.queue.add.priority_token_issued'), code=400)
                if priority_token == TOKEN_ISSUE_ERROR.EVENT_END:
                    _log_event(status='reject', reason='event_end')
                    raise action_error(message=_('view.queue.add.event_end ${event_end}', mapping={'event_end': event_end}), code=400)
                if priority_token == TOKEN_ISSUE_ERROR.TOKEN_ISSUED:
                    _log_event(status='reject', reason='token.already_issued')
                    raise action_error(message=_('view.queue.add.priority_token_already_issued'), code=400)
                _log_event(status='reject', reason='token.limit')
                raise action_error(message=_('view.queue.add.token_limit'), code=400)

    queue_item = QueueItem()
    for key, value in request.params.items():
        if hasattr(queue_item, key):
            setattr(queue_item, key, value)
    queue_item.queue_id = request.context.queue_id

    # Set session owner - if admin allow manual setting of session_owner via params
    if is_admin(request) and queue_item.session_owner:
        pass
    else:
        queue_item.session_owner = request.session['id']

    DBSession.add(queue_item)
    _log_event(status='ok', queue_id=queue_item.queue_id, track_id=queue_item.track_id, performer_name=queue_item.performer_name)
    #log.info('add - %s to queue by %s' % (queue_item.track_id, queue_item.performer_name))

    invalidate_cache(request, track_id)

    return action_ok(message='track queued', data={'queue_item.id': ''}, code=201)  # TODO: should return 201 and have id of newly created object. data={'track':{'id':}}


#@view_config(route_name='queue', custom_predicates=(method_delete_router, lambda info,request: request.params.get('queue_item.id')) ) #request_method='POST',
@view_config(
    context='karakara.traversal.QueueItemsContext',
    acquire_cache_bucket_func=acquire_cache_bucket_func,
    custom_predicates=(
        method_delete_router,
        lambda info, request: request.params.get('queue_item.id')
    )
)
@modification_action
def queue_item_del(request):
    """
    Remove items from the queue

    check session owner or admin
    state can be passed as "complete" to mark track as played

    TODO: THIS DOES NOT CONFORM TO THE REST STANDARD!!! Refactor
    """
    _log_event = partial(request.log_event, method='del')

    queue_item_id = int(request.params['queue_item.id'])
    queue_item = DBSession.query(QueueItem).get(queue_item_id)

    if not queue_item:
        _log_event(status='reject', reason='invalid.queue_item.id', queue_item_id=queue_item_id)
        raise action_error(message='invalid queue_item.id', code=404)
    if not is_admin(request) and queue_item.session_owner != request.session['id']:
        _log_event(status='reject', reason='not_owner', track_id=queue_item.track_id)
        raise action_error(message='you are not the owner of this queue_item', code=403)

    #DBSession.delete(queue_item)
    queue_item.status = request.params.get('status', 'removed')

    _log_event(status='ok', track_id=queue_item.track_id, queue_id=queue_item.queue_id)
    #log.info('remove - %s from queue' % (queue_item.track_id))
    #queue_item_track_id = queue_item.track_id  # Need to get queue_item.track_id now, as it will be cleared by invalidate_queue
    invalidate_cache(request, queue_item.track_id)

    return action_ok(message='queue_item status changed')


#@view_config(route_name='queue', custom_predicates=(method_put_router,))  # request_method='PUT'
@view_config(context='karakara.traversal.QueueItemsContext', custom_predicates=(method_put_router,))
@modification_action
def queue_item_update(request):
    """
    Used to touch queed items

    check session owner or admin

    TODO: THIS DOES NOT CONFORM TO THE REST STANDARD!!! Refactor
    """
    _log_event = partial(log_event, request, method='update')

    params = dict(request.params)

    for field in [f for f in ['queue_item.id', 'queue_item.move.target_id'] if f in params]:
        try:
            params[field] = int(params[field])
        except ValueError:
            raise action_error(message='invalid {0}'.format(field), code=404)

    queue_item_id = int(params['queue_item.id'])
    queue_item = DBSession.query(QueueItem).get(queue_item_id)

    if not queue_item:
        _log_event(status='reject', reason='invalid.queue_item.id', queue_item_id=queue_item_id)
        raise action_error(message='invalid queue_item.id', code=404)
    if not is_admin(request) and queue_item.session_owner != request.session['id']:
        _log_event(status='reject', reason='not_owner', track_id=queue_item.track_id)
        raise action_error(message='you are not the owner of this queue_item', code=403)

    # If moving, lookup new weighting from the target track id
    # The source is moved infront of the target_id
    if params.get('queue_item.move.target_id'):
        if not is_admin(request):
            _log_event(status='reject', reason='move.not_admin', queue_item_id=queue_item_id)
            raise action_error(message='admin only action', code=403)
        # get next and previous queueitem weights
        try:
            target_weight,  = DBSession.query(QueueItem.queue_weight).filter(QueueItem.id==params.pop('queue_item.move.target_id')).one()
            try:
                target_weight_next,  = DBSession.query(QueueItem.queue_weight).filter(QueueItem.queue_weight<target_weight).order_by(QueueItem.queue_weight.desc()).limit(1).one()
            except NoResultFound:
                target_weight_next = 0.0
            # calculate weight inbetween and inject that weight into the form params for saving
            params['queue_weight'] = (target_weight + target_weight_next) / 2.0
        except NoResultFound:
            log.debug('queue_item.move.target_id not found, assuming end of queue is the target')
            params['queue_weight'] = QueueItem.new_weight(DBSession)

    # Update any params to the db
    for key, value in params.items():
        if hasattr(queue_item, key):
            setattr(queue_item, key, value)
    queue_item.time_touched = datetime.datetime.now()  # Update touched timestamp

    #log.info('update - %s' % (queue_item.track_id))
    _log_event(status='ok', track_id=queue_item.track_id, queue_id=queue_item.queue_id)

    invalidate_cache(request, queue_item.track_id)

    return action_ok(message='queue_item updated')


@view_config(route_name='priority_tokens')
@admin_only
def priority_tokens(request):
    # TODO: karakara.queue.add.duplicate.time_limit is the wrong value to use here
    priority_tokens = DBSession.query(PriorityToken)\
        .filter(PriorityToken.valid_start >= now() - request.queue.settings.get('karakara.queue.add.duplicate.time_limit')) \
        .order_by(PriorityToken.valid_start)
    return action_ok(data={
        'priority_tokens': (priority_token.to_dict('full') for priority_token in priority_tokens),
    })
