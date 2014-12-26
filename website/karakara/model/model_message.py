from . import Base, JSONEncodedDict

from sqlalchemy import Column, Enum
from sqlalchemy import Unicode, UnicodeText, Integer, DateTime

import copy
import datetime
now = lambda: datetime.datetime.now()

__all__ = [
    "Message",
]

#_message_types = Enum('user', 'feedback', 'boardcast', name="message_types")


class Message(Base):
    """
    Message Framework

    A model for a persistant message log

    to is present and from is null = from admin to user
    to is null and from is null = admin broardcast to all users
    to is 'feedback' from is present = feedback

    """
    __tablename__   = "message"

    id              = Column(Integer(),  primary_key=True)
    #type            = Column(_message_types, nullable=False)
    session_id_from = Column(Unicode(), nullable=True)
    session_id_to   = Column(Unicode(), nullable=True)
    details         = Column(UnicodeText(), nullable=False, default="")
    timestamp       = Column(DateTime(), nullable=False, default=now)
    extra           = Column(JSONEncodedDict(), nullable=False, default={})

    __to_dict__ = copy.deepcopy(Base.__to_dict__)
    __to_dict__.update({
        'default': {
            'id'             : None,
            'session_id_from': None,
            'session_id_to'  : None,
            'timestamp'      : None,
            'message'        : None,
        },
    })

    __to_dict__.update({'full': copy.deepcopy(__to_dict__['default'])})
