from sqlalchemy.orm.exc import NoResultFound

from . import DBSession
from .model_tracks import Tag



def get_tag(tag):
    if isinstance(tag, Tag):
        return tag
    
    tag = tag.lower()
    
    
    try:
        return DBSession.query(Tag).filter_by(name=tag).one()
    except NoResultFound as nrf:
        t = Tag(tag)
        DBSession.add(t)
        return t
