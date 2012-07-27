from sqlalchemy.sql import null
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from . import DBSession
from .model_tracks import Tag

import logging
log = logging.getLogger(__name__)


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
            log.warn('multi parent tags need fully implementing for - %s' % tag)
            tag    = tag_string_split.pop()
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