from . import Base

from sqlalchemy     import Column
from sqlalchemy     import Integer, Unicode, DateTime, Boolean

import copy
import datetime
now = lambda: datetime.datetime.now()

__all__ = [
    "ComunityUser",
]


class ComunityUser(Base):
    """
    """
    __tablename__   = "comunity_user"

    id              = Column(Integer(), primary_key=True)
    name            = Column(Unicode(), nullable=True)
    email           = Column(Unicode(), nullable=True)
    timestamp       = Column(DateTime(), nullable=False, default=now)
    approved        = Column(Boolean(), nullable=False, default=False)
    
    __to_dict__ = copy.deepcopy(Base.__to_dict__)
    __to_dict__.update({
        'default': {
            'id'          : None ,
            'name'        : None ,
            'timestamp'   : None ,
            'approved'    : None ,
        },
    })
    
    __to_dict__.update({'full': copy.deepcopy(__to_dict__['default'])})
    __to_dict__['full'].update({
            'email'     : None ,
            
    })
