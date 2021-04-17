import datetime
from functools import partial
import srt
from typing import List, Dict, Any

from sqlalchemy.orm import joinedload, undefer, Query  # , joinedload_all
from sqlalchemy.orm.exc import NoResultFound

from pyramid.view import view_config

from calaldees.date_tools import now
from calaldees.data import subdict
from calaldees.json import json_string

from . import action_ok, action_error, is_admin, modification_action, admin_only

from ..model import DBSession
from ..model.model_queue import QueueItem, _queueitem_statuss
from ..model.model_tracks import Track
from ..model.model_priority_token import PriorityToken
from ..model.actions import get_track

from ..templates.helpers import track_title

from ..model_logic import QUEUE_DUPLICATE, TOKEN_ISSUE_ERROR
from ..model_logic.priority_token_logic import PriorityTokenManager

#from .track import invalidate_track

import logging
log = logging.getLogger(__name__)


def acquire_cache_bucket_func(request):
    return request.cache_manager.get(f'queue-{request.context.queue_id}')

def invalidate_cache(request, track_id: str) -> None:
    request.cache_bucket.invalidate(request=request)  # same as acquire_cache_bucket_func(request)
    request.cache_manager.get(f'queue-{request.context.queue_id}-track-{track_id}').invalidate(request=request)

    time_padding = request.queue.settings.get('karakara.queue.track.padding')
    queue_items = _queue_items_dict_with_track_dict(_queue_query(request.context.queue_id), time_padding)
    request.send_websocket_message('queue', json_string(queue_items), retain=True)

def _queue_query(queue_id: str) -> Query:
    return DBSession.query(QueueItem).filter(QueueItem.queue_id==queue_id).filter(QueueItem.status=='pending').order_by(QueueItem.queue_weight)

def _queue_items_dict_with_track_dict(queue_query: Query, time_padding: datetime.timedelta) -> List[Dict[str, Any]]:
    queue_dicts = [queue_item.to_dict('full') for queue_item in queue_query]

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
                            )
        tracks = {track['id']:track for track in [track.to_dict('full') for track in tracks]}

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

        # Convert SRT format lyrics in 'srt' property
        # into JSON format lyrics in 'lyrics' property
        try:
            if track['srt']:
                track['lyrics'] = [{
                    'id': line.index,
                    'text': line.content,
                    'start': line.start.total_seconds(),
                    'end': line.end.total_seconds(),
                } for line in srt.parse(track['srt'])]
        except Exception as e:
            log.exception(f"Error parsing subtitles for track {track['id']}")
        if 'lyrics' not in track:
            track['lyrics'] = []
        del track['srt']

    total_duration = datetime.timedelta(seconds=0)
    for queue_item in queue_dicts:
        # Attach track to queue_item
        queue_item['track'] = tracks.get(queue_item['track_id'], {})

        # Attach total_duration to queue_item
        if not queue_item['track']:
            continue
        queue_item['total_duration'] = total_duration
        total_duration += datetime.timedelta(seconds=queue_item['track']['duration']) + time_padding

    return queue_dicts


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
    def get_queue_dict() -> Dict[str, Any]:
        log.debug(f'cache gen - queue {request.cache_bucket.version}')
        time_padding = request.queue.settings.get('karakara.queue.track.padding')

        # Get queue order
        queue_dicts = _queue_items_dict_with_track_dict(_queue_query(request.context.queue_id), time_padding)

        # Calculate the index to split the queue list
        #  - non admin users do not see the whole queue in order.
        #  - after a specifyed time threshold, the quque order is obscured
        #  - it is expected that consumers of this api return will obscure the
        #    order passed the specifyed 'split_index'
        split_markers = list(request.queue.settings.get('karakara.queue.group.split_markers'))
        split_indexs = []
        total_duration = datetime.timedelta(seconds=0)
        for index, queue_item in enumerate(queue_dicts):
            if not queue_item['track']:
                continue
            total_duration += datetime.timedelta(seconds=queue_item['track']['duration']) + time_padding
            if split_markers and total_duration > split_markers[0]:
                split_indexs.append(index + 1)
                del split_markers[0]

        return {'queue': queue_dicts, 'queue_split_indexs': split_indexs}

    return action_ok(
        data=request.cache_bucket.get_or_create(get_queue_dict)
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
            raise action_error(message=f'no {field}', code=400)
    track_id = request.params.get('track_id')
    try:
        track = DBSession.query(Track).get(track_id)
        assert track
    except AssertionError:
        raise action_error(message=_('view.queue_item.add.error.track_id ${track_id}', mapping={'track_id': track_id}), code=400)

    # If not admin, check additional restrictions
    if not is_admin(request):
        performer_name = request.params.get('performer_name').strip()  # TODO: It would be good to ensure this value is writen to the db. However we cant modify the request.param dict directly. See creation of queueitem below

        # Valid performer name
        valid_performer_names = request.queue.settings.get('karakara.queue.add.valid_performer_names')
        if valid_performer_names and performer_name.lower() not in map(lambda name: name.lower(), valid_performer_names):
            message = _('view.queue_item.add.invalid_performer_name ${performer_name}', mapping=dict(
                performer_name=performer_name
            ))
            raise action_error(message, code=400)

        # TODO: Unify and tidy this shit .. Duplicate messages are very similat and can offload they db access to the model_logic.

        # Duplicate performer retractions
        queue_item_performed_tracks = request.queue.for_performer(performer_name)
        if queue_item_performed_tracks['performer_status'] == QUEUE_DUPLICATE.THRESHOLD:
            try:
                latest_track_title = get_track(queue_item_performed_tracks['queue_items'][0].track_id).title
            except Exception:
                latest_track_title = ''
            message = _('view.queue_item.add.dupicate_performer_limit ${performer_name} ${estimated_next_add_time} ${track_count} ${latest_queue_item_title}', mapping=dict(
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
            try:
                latest_track_title = get_track(queue_item_tracks_queued['queue_items'][0].track_id).title
            except Exception:
                latest_track_title = ''
            message = _('view.queue_item.add.dupicate_track_limit ${track_id} ${estimated_next_add_time} ${track_count} ${latest_queue_item_title}', mapping=dict(
                track_id=track.id,
                latest_queue_item_title=latest_track_title,
                **subdict(queue_item_tracks_queued, {
                    'estimated_next_add_time',
                    'track_count',
                })
            ))
            _log_event(status='reject', reason='duplicate.track', message=message)
            raise action_error(message=message, code=400)

        # Event start time
        event_start = request.queue.settings.get('karakara.event.start')
        if event_start and now() < event_start:
            log.debug('event start restricted')
            _log_event(status='reject', reason='event_start')
            raise action_error(message=_('view.queue_item.add.event_start ${event_start}', mapping={'event_start': event_start}), code=400)

        # Event end time
        event_end = request.queue.settings.get('karakara.event.end')
        if event_end and now() + request.queue.duration > event_end:
            log.debug('event end restricted')
            _log_event(status='reject', reason='event_end')
            raise action_error(message=_('view.queue_item.add.event_end ${event_end}', mapping={'event_end': event_end}), code=400)

        # Queue time limit
        queue_limit = request.queue.settings.get('karakara.queue.add.limit')
        if queue_limit and request.queue.duration > queue_limit:
            # If no device priority token - issue token and abort
            # else consume the token and proceed with addition
            priority_token_manager = PriorityTokenManager(request)
            if not priority_token_manager.consume():
                # Issue a priority token
                priority_token = priority_token_manager.issue()
                if isinstance(priority_token, PriorityToken):
                    _log_event(status='reject', reason='token.issued')
                    raise action_error(message=_('view.queue_item.add.priority_token_issued'), code=400)
                if priority_token == TOKEN_ISSUE_ERROR.EVENT_END:
                    _log_event(status='reject', reason='event_end')
                    raise action_error(message=_('view.queue_item.add.event_end ${event_end}', mapping={'event_end': event_end}), code=400)
                if priority_token == TOKEN_ISSUE_ERROR.TOKEN_ISSUED:
                    _log_event(status='reject', reason='token.already_issued')
                    raise action_error(message=_('view.queue_item.add.priority_token_already_issued'), code=400)
                _log_event(status='reject', reason='token.limit')
                raise action_error(message=_('view.queue_item.add.token_limit'), code=400)

    queue_item = QueueItem()
    for key, value in request.params.items():  # TODO: strip() the performer_name?
        if hasattr(queue_item, key):
            setattr(queue_item, key, value)
    queue_item.queue_id = request.context.queue_id

    # Set session owner - if admin allow manual setting of session_owner via params
    if is_admin(request) and queue_item.session_owner:
        pass
    else:
        queue_item.session_owner = request.session_identity['id']

    DBSession.add(queue_item)
    _log_event(status='ok', queue_id=queue_item.queue_id, track_id=queue_item.track_id, performer_name=queue_item.performer_name)
    #log.info('add - %s to queue by %s' % (queue_item.track_id, queue_item.performer_name))

    message_data = {'track_id': queue_item.track_id, 'performer_name': queue_item.performer_name}
    invalidate_cache(request, track_id)

    return action_ok(
        message=_('view.queue_item.add.ok ${track_id} ${performer_name}', mapping=message_data),
        data={'queue_item.id': ''},
        code=201,
    )  # TODO: should return 201 and have id of newly created object. data={'track':{'id':}}


#@view_config(route_name='queue', custom_predicates=(method_delete_router, lambda info,request: request.params.get('queue_item.id')) ) #request_method='POST',
@view_config(
    context='karakara.traversal.QueueItemsContext',
    acquire_cache_bucket_func=acquire_cache_bucket_func,
    method_router='DELETE',
    requires_param='queue_item.id',
)
@modification_action
def queue_item_del(request):
    """
    Remove items from the queue

    check session owner or admin
    state can be passed as "complete" to mark track as played

    TODO: THIS DOES NOT CONFORM TO THE REST STANDARD!!! Refactor
    """
    _ = request.translate
    _log_event = partial(request.log_event, method='del')

    queue_item_id = int(request.params['queue_item.id'])
    queue_item = DBSession.query(QueueItem).get(queue_item_id)

    if not queue_item:
        _log_event(status='reject', reason='invalid.queue_item.id', queue_item_id=queue_item_id)
        raise action_error(message='invalid queue_item.id', code=404)
    if not is_admin(request) and queue_item.session_owner != request.session_identity['id']:
        _log_event(status='reject', reason='not_owner', track_id=queue_item.track_id)
        raise action_error(
            message=_(
                'view.queue_item.error.not_owner ${track_id} ${session_owner}',
                mapping={'track_id': queue_item.track_id, 'session_owner': queue_item.session_owner},
            ),
            code=403,
        )

    first_queue_item_id = _queue_query(request.context.queue_id).limit(1).one().id
    if first_queue_item_id == queue_item_id:
        # TODO: Consider if this is client side logic or server side logic.
        # BUG: Currently player.js surpress's queue_update events while it is playing a video.
        #      Broken Flow: queue 3 tracks - play - delete queue_item (thats not playing) - stop - player queue is out of date
        request.send_websocket_message('commands', 'stop')
        # The impending invalidate_cache() will update the client queue

    #DBSession.delete(queue_item)
    queue_item.status = request.params.get('status', 'removed')

    _log_event(status='ok', track_id=queue_item.track_id, queue_id=queue_item.queue_id)
    #log.info('remove - %s from queue' % (queue_item.track_id))
    #queue_item_track_id = queue_item.track_id  # Need to get queue_item.track_id now, as it will be cleared by invalidate_queue
    message_data = {'track_id': queue_item.track_id, 'queue_id': queue_item.queue_id}
    invalidate_cache(request, queue_item.track_id)

    return action_ok(
        message=_('view.queue_item.delete.ok ${track_id} ${queue_id}', mapping=message_data)
    )


#@view_config(route_name='queue', custom_predicates=(method_put_router,))  # request_method='PUT'
@view_config(
    context='karakara.traversal.QueueItemsContext',
    method_router='PUT',
    acquire_cache_bucket_func=acquire_cache_bucket_func,
)
@modification_action
def queue_item_update(request):
    """
    Used to touch queed items

    check session owner or admin

    TODO: THIS DOES NOT CONFORM TO THE REST STANDARD!!! Refactor
    """
    _ = request.translate
    _log_event = partial(request.log_event, method='update')

    params = dict(request.params)

    for field in [f for f in ['queue_item.id', 'queue_item.move.target_id'] if f in params]:
        try:
            params[field] = int(params[field])
        except ValueError:
            raise action_error(message=f'invalid {field}', code=404)
    status = params.get('status')
    if status and status not in _queueitem_statuss.enums:
        raise action_error(message=f'invalid queue_item.status {status} - valid values are {_queueitem_statuss.enums}', code=400)

    queue_item_id = int(params['queue_item.id'])
    queue_item = DBSession.query(QueueItem).get(queue_item_id)

    if not queue_item:
        _log_event(status='reject', reason='invalid.queue_item.id', queue_item_id=queue_item_id)
        raise action_error(message='invalid queue_item.id', code=404)
    if not is_admin(request) and queue_item.session_owner != request.session_identity['id']:
        _log_event(status='reject', reason='not_owner', track_id=queue_item.track_id)
        raise action_error(
            message=_(
                'view.queue_item.error.not_owner ${track_id} ${session_owner}',
                mapping={'track_id': queue_item.track_id, 'session_owner': queue_item.session_owner},
            ),
            code=403,
        )

    # If moving, lookup new weighting from the target track id
    # The source is moved infront of the target_id
    if params.get('queue_item.move.target_id'):
        if not is_admin(request):
            _log_event(status='reject', reason='move.not_admin', queue_item_id=queue_item_id)
            raise action_error(
                message=_('view.admin_required'),
                code=403,
            )
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

    message_data = {'track_id': queue_item.track_id, 'queue_item_id': queue_item.id}  # Because invalidate expunges objects in the session
    invalidate_cache(request, queue_item.track_id)

    return action_ok(
        message=_('view.queue_item.update.ok ${track_id} ${queue_item_id}', mapping=message_data)
    )


@view_config(
    context='karakara.traversal.QueuePriorityTokenContext',
)
@admin_only
def priority_tokens(request):
    # TODO: karakara.queue.add.duplicate.time_limit is the wrong value to use here
    priority_tokens = DBSession.query(PriorityToken)\
        .filter(PriorityToken.valid_start >= now() - request.queue.settings.get('karakara.queue.add.duplicate.time_limit')) \
        .order_by(PriorityToken.valid_start)
    return action_ok(data={
        'priority_tokens': tuple(priority_token.to_dict('full') for priority_token in priority_tokens),
    })
