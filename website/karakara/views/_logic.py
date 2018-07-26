"""
Common View Logic
  - common place for logic and complex querys that often appear duplicated across the system
  
The rational behind placing these in the views is because they can acess pyramid settings.
Acess to settings does not belong in the model
"""
import datetime
import json

from sqlalchemy import or_, and_
from sqlalchemy.orm.exc import NoResultFound

from calaldees..misc import now, json_object_handler

from karakara.model.model_queue import QueueItem
from karakara.model.model_priority_token import PriorityToken

import logging
log = logging.getLogger(__name__)


__all__ = [
    'queue_item_for_performer',
    'queue_item_for_track',
    'QUEUE_DUPLICATE',
    'TOKEN_ISSUE_ERROR',
    'issue_priority_token',
]


# Constants ----------


# Methods -----------

