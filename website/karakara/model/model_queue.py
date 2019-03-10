from . import Base

from sqlalchemy import event, Column, Enum, ForeignKey, String, Unicode, Integer, DateTime, Float
from sqlalchemy.orm import relationship, backref, Session
from sqlalchemy.orm.exc import NoResultFound

import enum
import copy

import datetime
now = lambda: datetime.datetime.now()

__all__ = [
    "QueueItem", "QueueItemStatus",
]


class QueueItemStatus(enum.Enum):
    PENDING = "pending"
    PLAYED = "played"
    SKIPPED = "skipped"
    REMOVED = "removed"



class Queue(Base):
    __tablename__   = "queue"

    __to_dict__ = copy.deepcopy(Base.__to_dict__)
    __to_dict__.update({
        'default': {
            'id': None,
        },
    })
    __to_dict__.update({'full': copy.deepcopy(__to_dict__['default'])})
    __to_dict__['full'].update({
    })

    id = Column(String(), primary_key=True)


class QueueSetting(Base):
    """
    Each queue will have it's own configuration
    """
    __tablename__   = "queue_setting"

    id = Column(Integer(), primary_key=True)

    queue_id = Column(String(), ForeignKey('queue.id'), nullable=False)
    key = Column(String(), nullable=False)
    value = Column(String())


class QueueItem(Base):
    """
    queue_weight - rational and description
    The id will never change, but the queue will be sorted by this weight
    An admin can change the order of the queue,
    The algorithm with list the queued items in weight order and set the
    new weight to be in-between the prev,next queued item values.
    This supports order but without changing the primary key
    To ensure the queue_weight is set appropriately, a pre save handler will
    query the to find an apropiate values on first save
    """
    __tablename__   = "queue_item"

    id = Column(Integer(), primary_key=True)

    queue_id = Column(String(), ForeignKey('queue.id'), nullable=False)
    track_id = Column(String(), ForeignKey('track.id'), nullable=False)

    performer_name = Column(Unicode(), nullable=True, default="Untitled")
    session_owner = Column(Unicode(), nullable=True)

    queue_weight = Column(Float(), index=True, nullable=False)  # this by default is set to the id on first save,

    time_added = Column(DateTime(), nullable=False, default=now)
    time_touched = Column(DateTime(), nullable=False, default=now)

    status = Column(Enum(QueueItemStatus, name="status_types"), nullable=False, default="pending")

    # AllanC - there is no linking of the models now. Track and Queue are linked at an API level and can be in two separate DB's
    #track           = relationship("Track", backref=backref('queued')) # # AllanC - this makes the queue aware of the track and tightens coupleling ... ultimatelty the que and tracks should be in differnt db's but then the sqla links wont function ... think neo!!

    __to_dict__ = copy.deepcopy(Base.__to_dict__)
    __to_dict__.update({
        'default': {
            'id': None,
            'queue_id': None,
            'track_id': None,
            'performer_name': None,
            'time_touched': None,
            'time_added': None,
            'queue_weight': None,
        },
    })

    __to_dict__.update({'full': copy.deepcopy(__to_dict__['default'])})
    __to_dict__['full'].update({
            'status': lambda item: item.status.value,
            'session_owner': None,
            #'track'       : lambda queue_item: queue_item.track.to_dict(include_fields='attachments'),
            #'image'       : lambda queue_item: single_image(queue_item),    # AllanC - if you use this ensure you have setup eager loading on your query
    })

    @staticmethod
    def new_weight(DBSession):
        """
        Find the biggest queue weight possible and increment.
        Used when creating new queue items or moving items in the list beyond the last element
        """
        try:
            (max_weight,) = DBSession.query(QueueItem.queue_weight).order_by(QueueItem.queue_weight.desc()).limit(1).one()
        except NoResultFound:
            max_weight = 0.0
        return max_weight + 1.0

    @staticmethod
    def before_insert_listener(mapper, connection, target):
        """
        Event to set weight of queued item before first commit.
        Find the maximum 'weight' in the database
        This queue item weight will be set to max_weight + 1.0

        TODO: This is a bug waiting to happen. Now we have multiple queue this value could skyrocket.
              We need a way of getting the max weight per queue.
        """
        if not target.queue_weight:
            target.queue_weight = QueueItem.new_weight(Session(bind=connection))

event.listen(QueueItem, 'before_insert', QueueItem.before_insert_listener)
