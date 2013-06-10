from . import Base, JSONEncodedDict

from sqlalchemy     import event
from sqlalchemy     import Column, Enum, ForeignKey
from sqlalchemy     import String, Unicode, UnicodeText, Integer, Float
from sqlalchemy.orm import relationship, backref

import copy

__all__ = [
    "Track", "Tag", "Attachment", "_attachment_types",
]

_attachment_types = Enum("video","preview","thumbnail","subtitle", name="attachment_types")


class TrackTagMapping(Base):
    __tablename__ = "map_track_to_tag"
    track_id      = Column(String(),     ForeignKey('track.id')     , nullable=False, primary_key=True)
    tag_id        = Column(Integer(),    ForeignKey('tag.id')       , nullable=False, primary_key=True)

class TrackAttachmentMapping(Base):
    __tablename__ = "map_track_to_attachment"
    track_id      = Column(String(),     ForeignKey('track.id')     , nullable=False, primary_key=True)
    attachment_id = Column(Integer(),    ForeignKey('attachment.id'), nullable=False, primary_key=True)


class Track(Base):
    """
    """
    __tablename__   = "track"

    id              = Column(String(),      primary_key=True)
    #title           = Column(Unicode(),     nullable=False, default="Untitled")
    #description     = Column(Unicode(),     nullable=False, default="")
    duration        = Column(Float(),       nullable=False, default=0, doc="Duration in seconds")
    source_filename = Column(Unicode(),     nullable=True)
    
    tags            = relationship("Tag"       , secondary=TrackTagMapping.__table__)
    attachments     = relationship("Attachment", secondary=TrackAttachmentMapping.__table__)
    lyrics          = relationship("Lyrics")
    
    def tags_with_parents_dict(self):
        t = {None:[tag.name for tag in self.tags if not tag.parent]}
        for parent_name,tag_name in [(tag.parent.name,tag.name) for tag in self.tags if tag.parent]:
            if not t.get(parent_name):
                t[parent_name] = [tag_name]
            else:
                t[parent_name].append(tag_name)
        return t

    # TODO - Event to activate before save to DB to render the title from tags
    
    @property
    def title(self):
        """
        'title' is a tag
        tracks COULD have more than one title (english name and japanise name)
        This just returns the first one matched
        """
        try:
            return next(filter(lambda tag: tag.parent=='title', self.tags))
        except StopIteration:
            return ''

    #@title.setter
    #def title(self, value):
    #    self._x = value
    #@title.deleter
    #def title(self):
    #    #del self._x    
    
    @property
    def image(self):
        for attachment in self.attachments:
            if attachment.type == 'thumbnail':
                return attachment.location
        return ''
    
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
            'tags'        : lambda track: track.tags_with_parents_dict(),
            'lyrics'      : lambda track: [lyrics.to_dict() for lyrics in track.lyrics] ,
            'image'       : None ,
    })


class Tag(Base):
    """
    """
    __tablename__   = "tag"
    
    id            = Column(Integer(),  primary_key=True)
    name          = Column(Unicode(),  nullable=False, index=True)
    parent_id     = Column(Integer(),  ForeignKey('tag.id'), nullable=True, index=True)
    
    parent        = relationship('Tag',  backref=backref('children'), remote_side='tag.c.id')

    __to_dict__ = copy.deepcopy(Base.__to_dict__)
    __to_dict__.update({
        'default': {
    #Base.to_dict_setup(self, list_type='default', field_processors={
            'id'           : None ,
            'name'         : None , #lambda tag: str(tag)
        },
    })
    
    __to_dict__.update({'full': copy.deepcopy(__to_dict__['default'])})
    __to_dict__['full'].update({
    #Base.to_dict_setup(self, list_type='full', clone_list='default', filed_processors={
            'parent' : lambda track: track.parent.name ,
            'full'   : lambda track: '%s:%s' % (track.parent.name, track.name) if track.parent else track.name,
    })


    def __init__(self, name=None, parent=None):
        #print("Making new tag as %s:%s" % (name,parent))
        self.name = name
        if parent:
            assert isinstance(parent,Base)
            self.parent = parent

    def __str__(self):
        if self.parent:
            return '%s:%s' % (self.parent.name,self.name)
        return self.name

    @staticmethod
    def before_insert_listener(mapper, connection, target):
        """
        Event to ensure all tags are inserted lower case only
        because all searches are normalized to lower case
        """
        target.name = target.name.lower()

event.listen(Tag, 'before_insert', Tag.before_insert_listener)

class Attachment(Base):
    """
    """
    __tablename__   = "attachment"

    id              = Column(Integer(),         primary_key=True)
    location        = Column(Unicode(),         nullable=False)
    type            = Column(_attachment_types, nullable=False)
    extra_fields    = Column(JSONEncodedDict(), nullable=False, default={}) #mutable=True

    __to_dict__ = copy.deepcopy(Base.__to_dict__)
    __to_dict__.update({
        'default': {
            'id'           : None ,
            'location'     : None ,
            'type'         : None ,
            'extra_fields' : None ,
        },
    })
    __to_dict__.update({'full': copy.deepcopy(__to_dict__['default'])})
    __to_dict__['full'].update({
    })


class Lyrics(Base):
    """
    """
    __tablename__   = "lyrics"

    id              = Column(Integer()    , primary_key=True)
    track_id        = Column(String(),      ForeignKey('track.id'), nullable=False)
    language        = Column(String(4)    , nullable=False, default='eng')
    content         = Column(UnicodeText())
    
    __to_dict__ = copy.deepcopy(Base.__to_dict__)
    __to_dict__.update({
        'default': {
            'id'           : None ,
            'language'     : None ,
            'content'      : None ,
        },
    })
    __to_dict__.update({'full': copy.deepcopy(__to_dict__['default'])})
    __to_dict__['full'].update({
    })
