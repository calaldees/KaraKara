from . import Base

from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy import String, Unicode, Integer, DateTime

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
    
    track_id        = Column(Integer(),    ForeignKey('track.id'), nullable=False)
    
    performer_name  = Column(Unicode(250), nullable=True, default="Untitled")
    session_owner   = Column(Unicode(250), nullable=True)
    touched         = Column(DateTime()  , nullable=False, default=now)
    
    status          = Column(_queueitem_statuss ,  nullable=False, default="pending")
