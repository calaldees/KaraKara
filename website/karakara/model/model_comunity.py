from . import Base, JSONEncodedDict

from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy import Integer, Unicode, DateTime, Boolean
from sqlalchemy.orm import relationship

import copy
import datetime
now = lambda: datetime.datetime.now()

__all__ = [
    "ComunityUser",
]

# This is probably better as a db table
_provider_types = Enum('facebook', 'google', 'twitter', 'janrain', 'gigya', 'persona', 'test_provider', name='provider_types')


class ComunityUser(Base):
    """
    """
    __tablename__ = "comunity_user"

    id        = Column(Integer(), primary_key=True)
    name      = Column(Unicode(), nullable=True)
    email     = Column(Unicode(), nullable=True)
    timestamp = Column(DateTime(), nullable=False, default=now)
    approved  = Column(Boolean(), nullable=False, default=False)

    tokens    = relationship("SocialToken", cascade="all, delete-orphan")

    @property
    def user_data(self):
        if self.tokens:
            return self.tokens[0].data
        return {}

    __to_dict__ = copy.deepcopy(Base.__to_dict__)
    __to_dict__.update({
        'default': {
            'id'       : None,
            'name'     : None,
            'email'    : None,
            'timestamp': None,
            'approved' : None,
        },
    })

    __to_dict__.update({'full': copy.deepcopy(__to_dict__['default'])})
    __to_dict__['full'].update({
    })


class SocialToken(Base):
    """
    """
    __tablename__ = 'social_token'

    id       = Column(Integer(), primary_key=True)
    user_id  = Column(Integer(), ForeignKey('comunity_user.id'), nullable=False)
    token    = Column(Unicode(), nullable=False, index=True)
    provider = Column(_provider_types, nullable=False)
    data     = Column(JSONEncodedDict(), nullable=False, default={})
