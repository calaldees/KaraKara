from . import Base

from sqlalchemy import Column
from sqlalchemy import Unicode, Integer, DateTime, Boolean

__all__ = [
    "PriorityToken",
]

import copy

from externals.lib.misc import now


class PriorityToken(Base):
    """
    Client devices can be given priority tokens
    Once a device has a token, they are given priority when selecting a track
    during a specific issued time period.
    The server has to keep track of the tokens issued to validate when a
    priority request if made.
    """
    __tablename__ = "priority_tokens"

    id              = Column(Integer() , primary_key=True)
    issued          = Column(DateTime(), nullable=False, default=now)
    used            = Column(Boolean() , nullable=False, default=False)
    session_owner   = Column(Unicode() , nullable=False)
    valid_start     = Column(DateTime(), nullable=False)
    valid_end       = Column(DateTime(), nullable=False)

    __to_dict__ = copy.deepcopy(Base.__to_dict__)
    __to_dict__.update({
        'default': {
            #'id'         : None,
            #'issued'     : None,
            'valid_start': None,
            'valid_end'  : None,
        },
    })
    __to_dict__.update({'full': copy.deepcopy(__to_dict__['default'])})
    __to_dict__['full'].update({
        'id': None,
        'issued': None,
        'used': None,
        'session_owner': None,
    })
