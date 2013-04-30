import datetime
from pyramid.view import view_config

from . import web, etag, method_delete_router, is_admin

from ..lib.auto_format    import action_ok, action_error
from ..lib.pyramid_helpers import get_setting
from ..model              import DBSession, commit
from ..model.model_queue  import QueueItem
from ..model.model_tracks import Track

from ..templates.helpers import track_title

from sqlalchemy.orm     import joinedload, joinedload_all
from sqlalchemy.orm.exc import NoResultFound

import logging
log = logging.getLogger(__name__)

# Fake Etag placeholder
from ..lib.misc import random_string
queue_instance_id = None
def queue_updated():
    global queue_instance_id
    queue_instance_id = random_string()
queue_updated()
def queue_etag(request):
    global queue_instance_id
    return queue_instance_id + request.session.get('id','') + str(request.session.get('admin',False)) + str(request.session.peek_flash())

#-------------------------------------------------------------------------------
# Queue
#-------------------------------------------------------------------------------

@view_config(route_name='queue', request_method='GET')
@etag(queue_etag)
@web
def queue_view(request):
    """
    view current queue
    """
    queue = DBSession.query(QueueItem).filter(QueueItem.status=='pending').order_by(QueueItem.queue_weight).all()
    queue = [queue_item.to_dict('full') for queue_item in queue]
    
    trackids = [queue_item['track_id'] for queue_item in queue]    
    tracks   = DBSession.query(Track).\
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
    
    for queue_item in queue:
        queue_item['track'] = tracks[queue_item['track_id']]
    
    return action_ok(data={'queue':queue})


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
    
    duplicate_allow     = get_setting('karakara.queue.add.duplicate_allow'    , request, bool         )
    duplicate_threshold = get_setting('karakara.queue.add.duplicate_threshold', request, datetime.time)
    #existing_tracks_in_queue = DBSession.query(QueueItem).filter(QueueItem.track_id==track.id).filter(QueueItem.status!='removed').filter(QueueItem.time_touched>=datetime.datetime.now()-duplicate_threshold)
    
    queue_item = QueueItem()
    for key,value in request.params.items():
        if hasattr(queue_item, key):
            setattr(queue_item, key, value)
    
    queue_item.session_owner  = request.session['id']
    DBSession.add(queue_item)
    
    queue_updated() # Invalidate Cache
    
    log.info('%s added to queue by %s' % (queue_item.track_id, queue_item.performer_name))
    return action_ok(message='track queued')


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
    
    queue_updated() # Invalidate Cache
    
    return action_ok(message='queue_item status changed')


@view_config(route_name='queue', request_method='PUT')
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

    queue_updated() # Invalidate Cache

    return action_ok(message='queue_item updated')
