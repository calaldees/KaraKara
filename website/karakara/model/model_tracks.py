from . import Base

from sqlalchemy     import Column, Enum, ForeignKey
from sqlalchemy     import String, Unicode, Integer
from sqlalchemy.orm import relationship, backref

import copy

__all__ = [
    "Track", "Tag", "Attachment", "_attachment_types",
]

_attachment_types = Enum("image","preview","processed","subtitle", name="attachment_types")


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
    source_filename = Column(Unicode(250),     nullable=True)
    
    tags            = relationship("Tag"       , secondary=TrackTagMapping.__table__)
    attachments     = relationship("Attachment", secondary=TrackAttachmentMapping.__table__)
    
    queued          = relationship("QueueItem") # AllanC - this makes the track aware of the que and tightens coupleling ... ultimatelty the que and tracks should be in differnt db's
    
    
    __to_dict__ = copy.deepcopy(Base.__to_dict__)
    __to_dict__.update({
        'default': {
    #Base.to_dict_setup(self, list_type='default', field_processors={
            'id'           : None ,
            'title'        : None ,
            'duration'     : None ,
        },
    })
    
    __to_dict__.update({'full': copy.deepcopy(__to_dict__['default'])})
    __to_dict__['full'].update({
    #Base.to_dict_setup(self, list_type='full', clone_list='default', filed_processors={
            'description' : None ,
            'attachments' : lambda track: [attachment.to_dict() for attachment in track.attachments] ,
            'tags'        : lambda track: [tag.name for tag in track.tags],
    })


class Tag(Base):
    """
    """
    __tablename__   = "tag"
    
    id            = Column(Integer(),    primary_key=True)
    name          = Column(Unicode(100), nullable=False, index=True)
    parent_id     = Column(Integer(),    ForeignKey('tag.id'), nullable=True, index=True)
    
    parent        = relationship('Tag',  backref=backref('children'), remote_side='tag.c.id')

    __to_dict__ = copy.deepcopy(Base.__to_dict__)
    __to_dict__.update({
        'default': {
    #Base.to_dict_setup(self, list_type='default', field_processors={
            'id'           : None ,
            'name'         : None ,
        },
    })
    
    __to_dict__.update({'full': copy.deepcopy(__to_dict__['default'])})
    __to_dict__['full'].update({
    #Base.to_dict_setup(self, list_type='full', clone_list='default', filed_processors={
            'parent' : lambda track: track.parent.name ,
    })


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
    type            = Column(_attachment_types, nullable=False)

    __to_dict__ = copy.deepcopy(Base.__to_dict__)
    __to_dict__.update({
        'default': {
            'id'           : None ,
            'location'     : None ,
            'type'         : None ,
        },
    })
    __to_dict__.update({'full': copy.deepcopy(__to_dict__['default'])})
    __to_dict__['full'].update({
    })
