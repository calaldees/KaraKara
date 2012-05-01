from .models import Base

from sqlalchemy     import Column, ForeignKey, Enum
from sqlalchemy     import String, Unicode, Integer
from sqlalchemy.orm import relationship, backref




__all__ = [
    "Track", "Tag", "Attachment", "_attachment_types",
]

_attachment_types = Enum("image","preview","full","subtitle", name="attachment_types")


class TrackTagMapping(Base):
    __tablename__ = "map_track_to_tag"
    track_id      = Column(Integer(),    ForeignKey('track.id')     , nullable=False, primary_key=True)
    tag_id        = Column(Integer(),    ForeignKey('tag.id')       , nullable=False, primary_key=True)

class TrackAttachmentMapping(Base):
    __tablename__ = "map_track_to_attachment"
    track_id      = Column(Integer(),    ForeignKey('track.id')     , nullable=False, primary_key=True)
    attachment_id = Column(Integer(),    ForeignKey('attachment.id'), nullable=False, primary_key=True)



class Track(Base):
    """
    """
    __tablename__   = "track"

    id              = Column(String(32),       primary_key=True)
    title           = Column(Unicode(250),     nullable=False, default="Untitled")
    description     = Column(Unicode(250),     nullable=False, default="")
    duration        = Column(Integer(),        nullable=False, default=0, doc="Duration in seconds")
    
    tags            = relationship("Tag"       , secondary=TrackTagMapping.__table__)
    attachments     = relationship("Attachment", secondary=TrackAttachmentMapping.__table__)
    

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


class Attachment(Base):
    """
    """
    __tablename__   = "attachment"

    id              = Column(Integer(),         primary_key=True)
    location        = Column(Unicode(250),      nullable=False)
    status          = Column(_attachment_types, nullable=False)
