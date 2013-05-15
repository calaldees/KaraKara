from . import Base

from sqlalchemy     import Column, Enum, ForeignKey
from sqlalchemy     import String, Unicode, Integer, DateTime, Float, Boolean

__all__ = [
    "PriorityToken",
]

import datetime
now = lambda: datetime.datetime.now()



class PriorityToken(Base):
    """
    Client devices can be given priority tokens
    Once a device has a token, they are given priority when selecting a track
    during a specific issued time period.
    The server has to keep track of the tokens issued to validate when a
    priority request if made.
    """
    __tablename__   = "priority_tokens"

    id              = Column(Integer() , primary_key=True)
    issued          = Column(DateTime(), nullable=False, default=now)
    used            = Column(Boolean() , nullable=False, default=False)
    session_owner   = Column(Unicode() , nullable=False)
    start           = Column(DateTime(), nullable=False)
    end             = Column(DateTime(), nullable=False)
