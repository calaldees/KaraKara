from sqlalchemy.orm import joinedload

from . import DBSession
from .model_tracks import Tag, Track

import logging
log = logging.getLogger(__name__)


def rough_db_hash():
    """
    A SUPER quick, SUPER rough method of detecting a db change
    todo: Counting the tags is insufficent. A user might update a tag -> reimport -> tag count is the same
    suggestion: Could we get the last tag table update datetime?
    I've made a note in the model file - It should have one! Add this feature!
    """
    return 'tag_count:{0}'.format(str(DBSession.query(Tag).count()))


def get_track(id):
    return DBSession.query(Track).get(id)


def get_tag(tag, parent=None, create_if_missing=False):
    if not tag:
        return None
    if isinstance(tag, Tag):
        return tag

    tag = tag.lower().strip()

    # Extract parent from string in the format 'parent:tag'
    try   :
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

    # Check for single tag colision
    #if parent:
    #    try   : prefetch_tag_object = DBSession.query(Tag).filter_by(name=tag).filter_by(parent=null()).one()
    #    except: prefetch_tag_object = None
    #    if prefetch_tag_object and prefetch_tag_object.id != tag_object.id:
    #        print('COLISION!!!!')

    return tag_object


def clear_all_tracks():
    DBSession.query(Track).delete()
