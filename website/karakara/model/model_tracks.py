from .models import Base

from sqlalchemy     import Column, ForeignKey
from sqlalchemy     import String, Unicode, Integer
from sqlalchemy.orm import relationship, backref




__all__ = [
    "Track",
    "Tag",
    
]

class TrackTagMapping(Base):
    __tablename__ = "map_track_to_tag"
    track_id = Column(Integer(),    ForeignKey('track.id'), nullable=False, primary_key=True)
    tag_id   = Column(Integer(),    ForeignKey('tag.id')  , nullable=False, primary_key=True)



class Track(Base):
    """
    """
    __tablename__   = "track"

    id              = Column(String(32),       primary_key=True)
    title           = Column(Unicode(250),     nullable=False, default="Untitled")
    description     = Column(Unicode(250),     nullable=False, default="")
    duration        = Column(Integer(),        nullable=False, default=0, doc="Duration in seconds")
    
    tags            = relationship("Tag", secondary=TrackTagMapping.__table__)
    
    
class Tag(Base):
    """
    """
    __tablename__   = "tag"
    
    id            = Column(Integer(),    primary_key=True)
    name          = Column(Unicode(100), nullable=False, index=True)
    parent_id     = Column(Integer(),    ForeignKey('tag.id'), nullable=True, index=True)
    
    parent        = relationship('Tag',  backref=backref('children'), remote_side='tag.c.id')

    def __init__(self, name=None, parent=None):
        self.name = name
        if parent:
            assert isinstance(parent,Base)
            self.parent = parent
    