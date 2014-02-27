import datetime
import random

from pyramid.view import view_config

from externals.lib.misc import now

from . import web, action_ok, action_error, etag_decorator, cache, generate_cache_key, method_delete_router, method_put_router, is_admin, modification_action
from . import _logic

from ..model              import DBSession, commit
from ..model.model_queue  import QueueItem
from ..model.model_tracks import Track
from ..model.model_token  import PriorityToken

from ..templates.helpers import track_title

from sqlalchemy.orm     import joinedload  # , joinedload_all
from sqlalchemy.orm.exc import NoResultFound

from .tracks import invalidate_track

import logging
log = logging.getLogger(__name__)


#-------------------------------------------------------------------------------
# Cache Management
#-------------------------------------------------------------------------------
QUEUE_CACHE_KEY = 'queue'

queue_version = random.randint(0,2000000000)
def invalidate_queue(request=None):
    commit() # Before invalidating any cache data, ensure the new data is persisted
    global queue_version
    queue_version += 1
    cache.delete(QUEUE_CACHE_KEY)
    if request:
        request.registry['socket_manager'].recv('queue_updated'.encode('utf-8'))

#invalidate_queue()
def generate_cache_key_queue(request):
    global queue_version
    return '-'.join([generate_cache_key(request), str(queue_version)])

#-------------------------------------------------------------------------------
# Queue
#-------------------------------------------------------------------------------

@view_config(route_name='queue', request_method='GET')
@etag_decorator(generate_cache_key_queue)
@web
def queue_view(request):
    """
    view current queue
    """
    
    def get_queue_dict():
        log.debug('cache gen - queue {0}'.format(queue_version))
        
        # Get queue order
        queue_dicts = DBSession.query(QueueItem).filter(QueueItem.status=='pending').order_by(QueueItem.queue_weight)
        queue_dicts = [queue_item.to_dict('full') for queue_item in queue_dicts]
        
        # Fetch all tracks with id's in the queue
        trackids = [queue_item['track_id'] for queue_item in queue_dicts]
        tracks   = {}
        if trackids:
            tracks = DBSession.query(Track).\
                                filter(Track.id.in_(trackids)).\
                                options(\
                                    joinedload(Track.tags),\
                                    joinedload(Track.attachments),\
                                    joinedload('tags.parent'),\
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
            queue_item['track'] = tracks[queue_item['track_id']]
    
        # Calculate estimated track time
        # Overlay 'total_duration' on all tracks
        # It takes time for performers to change, so each track add a padding time
        #  +
        # Calculate the index to split the queue list
        #  - non admin users do not see the whole queue in order.
        #  - after a specifyed time threshold, the quque order is obscured
        #  - it is expected that consumers of this api return will obscure the
        #    order passed the specifyed 'split_index'
        split_markers = list(request.registry.settings.get('karakara.queue.group.split_markers'))
        time_padding = request.registry.settings.get('karakara.queue.track.padding')
        split_indexs = []
        total_duration = datetime.timedelta(seconds=0)
        for index, queue_item in enumerate(queue_dicts):
            queue_item['total_duration'] = total_duration
            total_duration += datetime.timedelta(seconds=queue_item['track']['duration']) + time_padding
            if split_markers and total_duration > split_markers[0]:
                split_indexs.append(index + 1)
                del split_markers[0]
        
        return {'queue':queue_dicts, 'queue_split_indexs':split_indexs}
    
    queue_data = cache.get_or_create(QUEUE_CACHE_KEY, get_queue_dict)
    return action_ok(data=queue_data)


@view_config(route_name='queue', request_method='POST')
@web
@modification_action
def queue_add(request):
    """
    Add items to end of queue
    """
    # Validation
    for field in ['track_id', 'performer_name']:
        if not request.params.get(field):
            raise action_error(message='no {0}'.format(field), code=400)
    track_id = request.params.get('track_id')
    try:
        track = DBSession.query(Track).get(track_id)
        assert track
    except AssertionError:
        raise action_error(message='track {0} does not exist'.format(track_id), code=400)
    
    # If not admin, check additional restrictions
    if not is_admin(request):
        # Duplucate performer resrictions
        performer_limit = request.registry.settings.get('karakara.queue.add.duplicate.performer_limit')
        if performer_limit:
            performer_name_count = _logic.queue_item_base_query(request, DBSession).filter(QueueItem.performer_name==request.params.get('performer_name')).count()
            if performer_name_count >= performer_limit:
                log.debug('duplicate performer restricted - {0}'.format(request.params.get('performer_name')))
                raise action_error(message='unable to queue track. duplicate "performer_name" limit reached', code=400)
        
        # Duplicate Addition Restrictions
        track_queued = _logic.queue_item_for_track(request, DBSession, track.id)
        if track_queued['status']==_logic.QUEUE_DUPLICATE.THRESHOLD:
            log.debug('duplicate track restricted - {0}'.format(track.id))
            raise action_error(message='unable to queue track. duplicate "track in queue" limit reached', code=400)
        
        # Max queue length restrictions
        queue_duration = _logic.get_queue_duration(request)
        
        # Event end time
        event_end = request.registry.settings.get('karakara.event.end')
        if event_end and now()+queue_duration > event_end:
            log.debug('event end restricted')
            raise action_error(message='Event will be ending soon and all the time has been alocated', code=400)
        
        # Queue time limit
        queue_limit = request.registry.settings.get('karakara.queue.add.limit')
        if queue_limit and queue_duration > queue_limit:
            # If no device priority token - issue token and abort
            # else consume the token and proceed with addition
            if not _logic.consume_priority_token(request, DBSession):
                # Issue a priority token
                priority_token = _logic.issue_priority_token(request, DBSession)
                if isinstance(priority_token, PriorityToken):
                    raise action_error(message='Queue limit reached - You have been given a priority token and will have priority to queue a track in your priority timeslot', code=400)
                if priority_token==_logic.TOKEN_ISSUE_ERROR.EVENT_END:
                    raise action_error(message='Event will be ending soon and all the time has been alocated', code=400)
                if priority_token==_logic.TOKEN_ISSUE_ERROR.TOKEN_ISSUED:
                    raise action_error(message='You already have a priority token timeslot. Queue your track when your timeslot occurs', code=400)
                raise action_error(message='Queue limit reached - try queing a track later', code=400)
    
    queue_item = QueueItem()
    for key,value in request.params.items():
        if hasattr(queue_item, key):
            setattr(queue_item, key, value)
    
    # Set session owner - if admin allow manual setting of session_owner via params
    if is_admin(request) and queue_item.session_owner:
        pass
    else:
        queue_item.session_owner = request.session['id']
    
    DBSession.add(queue_item)
    log.info('add - %s to queue by %s' % (queue_item.track_id, queue_item.performer_name))
    
    invalidate_queue(request) # Invalidate Cache
    invalidate_track(track_id)
    
    return action_ok(message='track queued', data={'queue_item.id':''}, code=201) #TODO: should return 201 and have id of newly created object. data={'track':{'id':}}


@view_config(route_name='queue', custom_predicates=(method_delete_router, lambda info,request: request.params.get('queue_item.id')) ) #request_method='POST',
@web
@modification_action
def queue_del(request):
    """
    Remove items from the queue
    
    check session owner or admin
    state can be passed as "complete" to mark track as played
    
    TODO: THIS DOES NOT CONFORM TO THE REST STANDARD!!! Refactor
    """
    queue_item = DBSession.query(QueueItem).get(int(request.params['queue_item.id']))

    if not queue_item:
        raise action_error(message='invalid queue_item.id', code=404)
    if not is_admin(request) and queue_item.session_owner != request.session['id']:
        raise action_error(message='you are not the owner of this queue_item', code=403)

    #DBSession.delete(queue_item)
    queue_item.status = request.params.get('status','removed')
    
    log.info('remove - %s from queue' % (queue_item.track_id))
    queue_item_track_id = queue_item.track_id
    
    invalidate_queue(request) # Invalidate Cache
    invalidate_track(queue_item_track_id)
    
    return action_ok(message='queue_item status changed')


@view_config(route_name='queue', custom_predicates=(method_put_router,) ) #request_method='PUT'
@web
@modification_action
def queue_update(request):
    """
    Used to touch queed items
    
    check session owner or admin
    
    TODO: THIS DOES NOT CONFORM TO THE REST STANDARD!!! Refactor
    """
    params = dict(request.params)
    
    for field in [f for f in ['queue_item.id', 'queue_item.move.target_id'] if f in params]:
        try:
            params[field] = int(params[field])
        except ValueError:
            raise action_error(message='invalid {0}'.format(field), code=404)
    
    queue_item = DBSession.query(QueueItem).get(params['queue_item.id'])

    if not queue_item:
        raise action_error(message='invalid queue_item.id', code=404)
    if not is_admin(request) and queue_item.session_owner != request.session['id']:
        raise action_error(message='you are not the owner of this queue_item', code=403)

    # If moving, lookup new weighting from the target track id
    # The source is moved infront of the target_id
    if params.get('queue_item.move.target_id'):
        if not is_admin(request):
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
    for key,value in params.items():
        if hasattr(queue_item, key):
            setattr(queue_item, key, value)
    queue_item.time_touched = datetime.datetime.now() # Update touched timestamp

    log.info('update - %s' % (queue_item.track_id))
    queue_item_track_id = queue_item.track_id

    invalidate_queue(request) # Invalidate Cache
    invalidate_track(queue_item_track_id)

    return action_ok(message='queue_item updated')
