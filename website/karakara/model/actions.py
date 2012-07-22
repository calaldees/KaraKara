from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import null

from . import DBSession
from .model_tracks import Tag



def get_tag(tag, parent=None):
    if not tag:
        return None
    if isinstance(tag, Tag):
        return tag
    
    tag = tag.lower().strip()
    
    # Extract parent from string in the format 'parent:tag'
    try   : parent, tag = tuple(tag.split(':'))
    except: pass
    
    if not tag:
        return None
    
    #print("get_tag(%s:%s)" % (parent,tag))
    
    #try:
    query = DBSession.query(Tag).filter_by(name=tag)
    if parent:
        query = query.join("parent", aliased=True).filter_by(name=parent)
    tag_object = query.order_by(Tag.id).all()
    if tag_object:
        tag_object = tag_object[-1]
    else:
    #except NoResultFound as nrf:
        tag_object = Tag(tag, get_tag(parent))
        DBSession.add(tag_object)

    # Check for single tag colision
    #if parent:
    #    try   : prefetch_tag_object = DBSession.query(Tag).filter_by(name=tag).filter_by(parent=null()).one()
    #    except: prefetch_tag_object = None
    #    if prefetch_tag_object and prefetch_tag_object.id != tag_object.id:
    #        print('COLISION!!!!')

    return tag_object