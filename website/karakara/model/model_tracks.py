from .models import Base

from sqlalchemy import Column
from sqlalchemy import String, Unicode, Integer




__all__ = [
    "Track",
]


class Track(Base):
    """
    """
    __tablename__   = "track"

    id              = Column(String(32),        primary_key=True)
    
    title           = Column(Unicode(250),     nullable=False, default="Untitled")
    description     = Column(Unicode(250),     nullable=False, default="")
    
    duration        = Column(Integer(),     nullable=False, default="")
    
    #requests = relationship("ItemRequest"  , backref=backref('item'), cascade="all,delete-orphan")
