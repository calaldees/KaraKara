from . import Base, JSONEncodedDict

from sqlalchemy import event
from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy import String, Unicode, UnicodeText, Integer, Float, DateTime
from sqlalchemy.orm import relationship, backref

import copy

import datetime
now = lambda: datetime.datetime.now()


__all__ = [
    "Track", "Tag", "Attachment", "_attachment_types",
]

_attachment_types = Enum('video', 'preview', 'srt', 'image', name="attachment_types")


class TrackTagMapping(Base):
    __tablename__ = "map_track_to_tag"
    track_id = Column(String(), ForeignKey('track.id'), nullable=False, primary_key=True)
    tag_id = Column(Integer(), ForeignKey('tag.id'), nullable=False, primary_key=True)


class TrackAttachmentMapping(Base):
    __tablename__ = "map_track_to_attachment"
    track_id = Column(String(), ForeignKey('track.id'), nullable=False, primary_key=True)
    attachment_id = Column(Integer(), ForeignKey('attachment.id'), nullable=False, primary_key=True)


class Track(Base):
    __tablename__ = "track"

    id = Column(String(), primary_key=True)
    duration = Column(Float(), nullable=False, default=0, doc="Duration in seconds")
    source_filename = Column(Unicode(), nullable=True)

    tags = relationship("Tag", secondary=TrackTagMapping.__table__)  # , lazy="joined"
    attachments = relationship("Attachment", secondary=TrackAttachmentMapping.__table__)
    #lyrics = relationship("Lyrics", cascade="all, delete-orphan")
    lyrics = Column(UnicodeText(), nullable=True)

    time_updated = Column(DateTime(), nullable=False, default=now)

    def tags_with_parents_dict(self):
        t = {None: [tag.name for tag in self.tags if not tag.parent]}
        for parent_name, tag_name in [(tag.parent.name, tag.name) for tag in self.tags if tag.parent]:
            if not t.get(parent_name):
                t[parent_name] = [tag_name]
            else:
                t[parent_name].append(tag_name)
        return t

    def get_tag(self, parent):
        tags_found = set()
        for tag in self.tags:
            if tag.parent and tag.parent.name == parent:
                tags_found.add(tag.name)
        return ' - '.join(sorted(tags_found))

    @property
    def title(self):
        """
        'title' is a tag
        tracks COULD have more than one title (english name and japanise name)
        This just returns the first one matched

        TODO - Event to activate before save to DB to render the title from tags
        """
        try:
            return next(filter(lambda tag: tag.parent.name == 'title' if tag.parent else False, self.tags)).name
        except StopIteration:
            return self.source_filename

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
            'source_filename': None ,
    })

    @staticmethod
    def before_update_listener(mapper, connection, target):
        """
        TODO: This may not be the whole story ...
          when tags/lyrics/attachments change then we want this to update as well
          Investigation needed.
          I think this is irrelevent any change will update the id and a
          new record will be created, so this can never happen.
        """
        target.time_updated = now()

event.listen(Track, 'before_update', Track.before_update_listener)



class Tag(Base):
    """
    """
    __tablename__ = "tag"

    id            = Column(Integer(),  primary_key=True)
    name          = Column(Unicode(),  nullable=False, index=True)
    parent_id     = Column(Integer(),  ForeignKey('tag.id'), nullable=True, index=True)

    parent        = relationship('Tag',  backref=backref('children'), remote_side='tag.c.id')  #  , lazy="joined", join_depth=3

    @property
    def full(self):
        return '{0}:{1}'.format(self.parent.name, self.name) if self.parent else self.name

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
            'full'   : None,
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

    # TODO: Hook for on updated/add/remove to update the time_updated on the track

event.listen(Tag, 'before_insert', Tag.before_insert_listener)


class Attachment(Base):
    """
    """
    __tablename__ = "attachment"

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

