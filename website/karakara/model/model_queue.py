from . import Base

from sqlalchemy     import Column, Enum, ForeignKey
from sqlalchemy     import String, Unicode, Integer, DateTime
from sqlalchemy.orm import relationship, backref

import copy

import datetime
now = lambda: datetime.datetime.now()

__all__ = [
    "QueueItem", "_queueitem_statuss",
]


_queueitem_statuss = Enum("pending", "complete", "removed", name="status_types")


class QueueItem(Base):
    """
    """
    __tablename__   = "queue"

    id              = Column(Integer(),        primary_key=True)
    
    track_id        = Column(String(32),    ForeignKey('track.id'), nullable=False)
    
    performer_name  = Column(Unicode(250), nullable=True, default="Untitled")
    session_owner   = Column(Unicode(250), nullable=True)
    touched         = Column(DateTime()  , nullable=False, default=now)
    
    status          = Column(_queueitem_statuss ,  nullable=False, default="pending")
    
    track           = relationship("Track", backref=backref('queued')) # # AllanC - this makes the queue aware of the track and tightens coupleling ... ultimatelty the que and tracks should be in differnt db's but then the sqla links wont function ... think neo!!

    __to_dict__ = copy.deepcopy(Base.__to_dict__)
    __to_dict__.update({
        'default': {
    #Base.to_dict_setup(self, list_type='default', field_processors={
            'id'            : None ,
            'track_id'      : None ,
            'performer_name': None ,
            'session_owner' : None ,
            'touched'       : None ,
        },
    })
    
    __to_dict__.update({'full': copy.deepcopy(__to_dict__['default'])})
    __to_dict__['full'].update({
            'track'       : lambda queue_item: queue_item.track.to_dict(include_fields='attachments'),
            'status'      : None,
            #'image'       : lambda queue_item: single_image(queue_item),    # AllanC - if you use this ensure you have setup eager loading on your query
    })
