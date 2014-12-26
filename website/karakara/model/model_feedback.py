"""
Marked for potential deprication
The new Message system could superceed this
"""
from . import Base, JSONEncodedDict

from sqlalchemy     import Column, Enum
from sqlalchemy     import Unicode, UnicodeText, Integer, DateTime

import copy
import datetime
now = lambda: datetime.datetime.now()

__all__ = [
    "Feedback", "_feedback_types",
]

_feedback_types = Enum("bug","feature","other", name="feedback_types")

class Feedback(Base):
    """
    """
    __tablename__   = "feedback"

    id              = Column(Integer(),  primary_key=True)
    #type            = Column(_feedback_types, nullable=False)
    
    contact         = Column(Unicode()    , nullable=True)
    details         = Column(UnicodeText(), nullable=False, default="")
    environ         = Column(JSONEncodedDict(), nullable=False, default={}) #mutable=True
    timestamp       = Column(DateTime(),  nullable=False, default=now)
    
    __to_dict__ = copy.deepcopy(Base.__to_dict__)
    __to_dict__.update({
        'default': {
            'id'          : None ,
            #'type'         : None ,
            'contact'     : None ,
            'details'     : None ,
            'timestamp'   : None ,
        },
    })
    
    __to_dict__.update({'full': copy.deepcopy(__to_dict__['default'])})
    __to_dict__['full'].update({
            'environ'     : None ,
    })
