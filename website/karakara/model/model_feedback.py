from . import Base, JSONEncodedDict

from sqlalchemy     import Column, Enum
from sqlalchemy     import String, Unicode, UnicodeText, Integer, Float

import copy

__all__ = [
    "Feedback", "_feedback_types",
]

_feedback_types = Enum("bug","feature","other", name="feedback_types")

class Feedback(Base):
    """
    """
    __tablename__   = "feedback"

    id              = Column(Integer(),  primary_key=True)
    type            = Column(_feedback_types, nullable=False)
    session_owner   = Column(Unicode(),   nullable=True)
    
    contact         = Column(Unicode()    , nullable=True)
    feedback        = Column(UnicodeText(), nullable=False, default="")
    
    __to_dict__ = copy.deepcopy(Base.__to_dict__)
    __to_dict__.update({
        'default': {
            'id'           : None ,
            'type'         : None ,
            'session_owner': None ,
            'feedback'     : None ,
        },
    })
    
    __to_dict__.update({'full': copy.deepcopy(__to_dict__['default'])})
    __to_dict__['full'].update({

    })
