import datetime
import random
from pyramid.view import view_config

from . import web, etag_decorator, cache, cache_none, generate_cache_key, method_delete_router, method_put_router, is_admin
from . import _logic

from ..lib.auto_format    import action_ok, action_error
from ..lib.misc           import now
from ..model              import DBSession, commit
from ..model.model_queue  import QueueItem
from ..model.model_tracks import Track

from ..templates.helpers import track_title

from sqlalchemy.orm     import joinedload, joinedload_all
from sqlalchemy.orm.exc import NoResultFound

from .tracks import invalidate_track

import logging
log = logging.getLogger(__name__)


#-------------------------------------------------------------------------------
# Cache Management
#-------------------------------------------------------------------------------
QUEUE_CACHE_KEY = 'queue'

queue_version = random.randint(0,65535)
def invalidate_queue():
    global queue_version
    queue_version += 1
    cache.delete(QUEUE_CACHE_KEY)
invalidate_queue()
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
        # Get queue order
        queue_dict = DBSession.query(QueueItem).filter(QueueItem.status=='pending').order_by(QueueItem.queue_weight)
        queue_dict = [queue_item.to_dict('full') for queue_item in queue_dict]
        
        # Fetch all tracks with id's in the queue
        trackids = [queue_item['track_id'] for queue_item in queue_dict]
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
        for queue_item in queue_dict:
            queue_item['track'] = tracks[queue_item['track_id']]
    
        # Calculate estimated track time
        # Overlay 'total_duration' on all tracks
        # It takes time for performers to change, so each track add a padding time
        time_padding = request.registry.settings.get('karakara.queue.template.padding')
        total_duration = datetime.timedelta(seconds=0)
        for queue_item in queue_dict:
            queue_item['total_duration'] = total_duration
            total_duration += datetime.timedelta(seconds=queue_item['track']['duration']) + time_padding
        
        return queue_dict
    
    queue_dict = cache.get_or_create(QUEUE_CACHE_KEY, get_queue_dict)
    return action_ok(data={'queue':queue_dict})


@view_config(route_name='queue', request_method='POST')
@web
def queue_add(request):
    """
    Add items to end of queue
    """
    # Validation
    for field in ['track_id', 'performer_name']:
        if not request.params.get(field):
            raise action_error(message='no {0}'.format(field), code=400)
    try:
        track = DBSession.query(Track).get(request.params.get('track_id'))
        assert track
    except AssertionError:
        raise action_error(message='track {0} does not exist'.format(request.params.get('track_id')), code=400)
    
    # If not admin, check additional restrictions
    if not is_admin(request):
        # Duplicate Addition Restrictions
        track_queued = _logic.queue_item_for_track(request, DBSession, track.id)
        if track_queued['status']==_logic.QUEUE_DUPLICATE.THRESHOLD:
            raise action_error(message='unable to queue track. duplicate "track in queue" limit reached', code=400)
        
        # Max queue length restrictions
        queue_duration = _logic.get_queue_duration(request)
        
        # Event end time
        event_end = request.registry.settings.get('karakara.event.end')
        if event_end and now()+queue_duration > event_end:
            raise action_error(message='event submissions are closed', code=400)
        
        # Queue time limit
        queue_limit = request.registry.settings.get('karakara.queue.add.limit')
        if queue_limit and queue_duration > queue_limit:
            # If no device priority token - issue token and abort
            # else consume the token and proceed with addition
            if not _logic.consume_priority_token(request, DBSession):
                # Issue a priority token
                priority_token = _logic.issue_priority_token(request, DBSession)
                if priority_token:
                    raise action_error(message='queue limit reached - priority token issued', code=400)
                raise action_error(message='queue limit reached', code=400)
    
    queue_item = QueueItem()
    for key,value in request.params.items():
        if hasattr(queue_item, key):
            setattr(queue_item, key, value)
    
    queue_item.session_owner  = request.session['id']
    DBSession.add(queue_item)
    
    invalidate_queue() # Invalidate Cache
    invalidate_track(track.id)
    
    log.info('%s added to queue by %s' % (queue_item.track_id, queue_item.performer_name))
    return action_ok(message='track queued') #TODO: should return 201 and have id of newly created object. data={'track':{'id':}}


@view_config(route_name='queue', custom_predicates=(method_delete_router, lambda info,request: request.params.get('queue_item.id')) ) #request_method='POST',
@web
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
    
    invalidate_queue() # Invalidate Cache
    invalidate_track(queue_item.track_id)
    
    return action_ok(message='queue_item status changed')


@view_config(route_name='queue', custom_predicates=(method_put_router,) ) #request_method='PUT'
@web
def queue_update(request):
    """
    Used to touch queed items
    
    check session owner or admin
    
    TODO: THIS DOES NOT CONFORM TO THE REST STANDARD!!! Refactor
    """
    params = dict(request.params)
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
        queue_item_target = DBSession.query(QueueItem).get(params.pop('queue_item.move.target_id'))
        try:
            target_weight_next,  = DBSession.query(QueueItem.queue_weight).filter(QueueItem.queue_weight<queue_item_target.queue_weight).order_by(QueueItem.queue_weight.desc()).limit(1).one()
        except NoResultFound:
            target_weight_next = 0.0
        # calculate weight inbetween and inject that weight into the form params for saving
        params['queue_weight'] = (queue_item_target.queue_weight + target_weight_next) / 2.0

    # Update any params to the db
    for key,value in params.items():
        if hasattr(queue_item, key):
            setattr(queue_item, key, value)
    queue_item.time_touched = datetime.datetime.now() # Update touched timestamp

    invalidate_queue() # Invalidate Cache
    invalidate_track(queue_item.track_id)

    return action_ok(message='queue_item updated')
