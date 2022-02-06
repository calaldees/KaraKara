import datetime
import operator

from calaldees.json import json_string

from sqlalchemy.orm import joinedload, undefer
from sqlalchemy.orm.exc import NoResultFound

from . import DBSession, commit
from .model_tracks import Tag, Track, TrackTagMapping, TrackAttachmentMapping
from .model_queue import Queue, QueueItem, QueueSetting

import logging
log = logging.getLogger(__name__)


def last_track_db_update():
    try:
        return DBSession.query(Track.time_updated).order_by(Track.time_updated.desc()).limit(1).one()[0]
    except NoResultFound:
        return datetime.datetime.utcfromtimestamp(0)


def get_track(id):
    return DBSession.query(Track).get(id)


def get_track_dict_full(id):
    try:
        return DBSession.query(Track).options(
            joinedload(Track.tags),
            joinedload(Track.attachments),
            joinedload('tags.parent'),
        ).get(id).to_dict('full')
    except AttributeError:
        return None


def get_tag(tag, parent=None, create_if_missing=False):
    if not tag:
        return None
    if isinstance(tag, Tag):
        return tag

    tag = tag.lower().strip()

    # Extract parent from string in the format 'parent:tag'
    try:
        tag_string_split = tag.split(':')
        if len(tag_string_split) == 2:
            parent, tag = tuple(tag_string_split)
        elif len(tag_string_split) > 2:
            tag = tag_string_split.pop()
            parent = tag_string_split.pop()
    except: pass

    if not tag:
        return None

    #print("get_tag(%s:%s)" % (parent,tag))

    #try:
    query = DBSession.query(Tag).filter_by(name=tag).options(joinedload(Tag.parent))
    if parent:
        query = query.join("parent", aliased=True).filter_by(name=parent)
    tag_object = query.order_by(Tag.id).all()
    if tag_object:
        tag_object = tag_object[-1]
    elif create_if_missing:
    #except NoResultFound as nrf:
        tag_object = Tag(tag, get_tag(parent, create_if_missing=create_if_missing))
        DBSession.add(tag_object)
        commit()

    # Check for single tag colision
    #if parent:
    #    try   : prefetch_tag_object = DBSession.query(Tag).filter_by(name=tag).filter_by(parent=null()).one()
    #    except: prefetch_tag_object = None
    #    if prefetch_tag_object and prefetch_tag_object.id != tag_object.id:
    #        print('COLISION!!!!')

    return tag_object


def _delete_cascade(_id, model, model_children, child_id_fieldname):
    attrgetter_child_id = operator.attrgetter(child_id_fieldname)
    for ModelClass in model_children:
        DBSession.query(ModelClass).filter(attrgetter_child_id(ModelClass) == _id).delete()
    DBSession.query(model).filter(model.id == _id).delete()


def delete_track(track_id):
    """
    Because we don't define the relationship between tracks and queue_items in the orm
    We need to manually handle the delete cascade
    Maybe we should consider using the orm? There is note on the QueueItem with more info
    However ... There may be a need to keep the queue separate ... for long
    running system we may remove tracks but we may want to keep a log of that
    were sang. There would be no track details, but currently the system will crash on html
    rendering if these queue_item orphan records are left
    """
    #attrgetter_track_id = operator.attrgetter('track_id')
    #for ModelClass in (QueueItem, TrackTagMapping, TrackAttachmentMapping):
    #    DBSession.query(ModelClass).filter(attrgetter_track_id(ModelClass) == track_id).delete()
    #DBSession.query(Track).filter(Track.id == track_id).delete()
    return _delete_cascade(track_id, Track, (QueueItem, TrackTagMapping, TrackAttachmentMapping), 'track_id')


def delete_queue(queue_id):
    return _delete_cascade(queue_id, Queue, (QueueItem, QueueSetting), 'queue_id')


def sync_all_queues_to_mqtt(registry):
    from . import DBSession
    from .model_queue import Queue

    for queue_obj in DBSession.query(Queue):
        sync_queue_to_mqtt(registry, queue_obj.id)


def sync_queue_to_mqtt(registry, queue_id):
    from socket import gaierror
    import paho.mqtt.client as mqtt
    from ..views.queue_items import _queue_items_dict_with_track_dict, _queue_query
    from ..views.queue_settings import _get_queue_settings

    MQTT_HOST = registry.settings['karakara.websocket.host'] # TODO: rename karakara.websocket.host to 'mqtt'?
    log.info(f"Syncing state for {queue_id} to {MQTT_HOST}")

    c = mqtt.Client()
    try:
        c.connect(MQTT_HOST)
    except gaierror:
        log.error(f'mqtt not running? {MQTT_HOST}:1883')
        return
    c.loop_start()

    settings = _get_queue_settings(registry, queue_id)
    msg = c.publish(f"karakara/room/{queue_id}/settings", json_string(settings), retain=True)
    msg.wait_for_publish()

    queue = _queue_items_dict_with_track_dict(_queue_query(queue_id), settings.get('karakara.queue.track.padding'))
    msg = c.publish(f"karakara/room/{queue_id}/queue", json_string(queue), retain=True)
    msg.wait_for_publish()
