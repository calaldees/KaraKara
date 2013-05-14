from . import Base

from sqlalchemy     import Column, Enum, ForeignKey
from sqlalchemy     import String, Unicode, Integer, DateTime, Float

__all__ = [
    "PriorityToken",
]



class PriorityToken(Base):
    """
    Client devices can be given priority tokens
    Once a device has a token, they are given priority when selecting a track
    during a specific issued time period.
    The server has to keep track of the tokens issued to validate when a
    priority request if made.
    """
    __tablename__   = "priority_tokens"

    id              = Column(Integer(),        primary_key=True)
