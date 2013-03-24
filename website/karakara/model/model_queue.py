from . import Base

from sqlalchemy     import Column, Enum, ForeignKey
from sqlalchemy     import String, Unicode, Integer, DateTime, Float
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
    
    queue_weight - rational and description
    The id will never change, but the queue will be sorted by this weight
    An admin can change the order of the queue,
    The algorithum with list the queed items in weight order and set the
    new weight to be inbetween the prev,next queued item values.
    This supports order but without changing the primary key
    To ensure the queue_weight is set approriately, a post save handler will
    query the to find an approriate values on first save
    
    
    """
    __tablename__   = "queue"

    id              = Column(Integer(),        primary_key=True)
    
    track_id        = Column(String(),    ForeignKey('track.id'), nullable=False)
    
    performer_name  = Column(Unicode(),   nullable=True, default="Untitled")
    session_owner   = Column(Unicode(),   nullable=True)
    
    queue_weight    = Column(Float()  ,   index=True) # nullable=False, # this by default is set to the id on first save,
    
    time_added      = Column(DateTime(),  nullable=False, default=now)
    time_touched    = Column(DateTime(),  nullable=False, default=now)
    
    status          = Column(_queueitem_statuss ,  nullable=False, default="pending")
    
    # AllanC - there is no linking of the models now. Track and Queue are linked at an API level and can be in two separate DB's
    #track           = relationship("Track", backref=backref('queued')) # # AllanC - this makes the queue aware of the track and tightens coupleling ... ultimatelty the que and tracks should be in differnt db's but then the sqla links wont function ... think neo!!
    
    __to_dict__ = copy.deepcopy(Base.__to_dict__)
    __to_dict__.update({
        'default': {
    #Base.to_dict_setup(self, list_type='default', field_processors={
            'id'            : None ,
            'track_id'      : None ,
            'performer_name': None ,
            'time_touched'  : None ,
            'time_added'    : None ,
            'queue_weight'  : None ,
        },
    })
    
    __to_dict__.update({'full': copy.deepcopy(__to_dict__['default'])})
    __to_dict__['full'].update({
            'status'       : None ,
            'session_owner': None ,
            #'track'       : lambda queue_item: queue_item.track.to_dict(include_fields='attachments'),
            #'image'       : lambda queue_item: single_image(queue_item),    # AllanC - if you use this ensure you have setup eager loading on your query
    })
