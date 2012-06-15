import random
import transaction

from ..model import DBSession
from ..lib.misc import random_string

from ..model.actions import get_tag
from ..model.model_tracks import Track, Tag, Attachment
from ..model.model_queue  import QueueItem

import logging
log = logging.getLogger(__name__)


def init_random_data(num_tracks=100):

    # Attachment generation ----------------------------------------------------
    attachments_meta = [
        ('preview1.3gp' , 'preview'  ),
        ('preview2.flv' , 'preview'  ),
        ('image1.jpg'   , 'image'    ),
        ('image2.jpg'   , 'image'    ),
        ('image3.png'   , 'image'    ),
        ('processed.mpg', 'processed'),
        ('subtitles.ssa', 'subtitle' ),
    ]
    attachments = []
    for location, type in attachments_meta:
        attachment = Attachment()
        attachment.location = location
        attachment.type     = type
        DBSession.add(attachment)
        attachments.append(attachment)
    
    
    # Random Tag generation ----------------------------------------------------
    parent_tag = get_tag('series')
    for series_num in range(10):
        DBSession.add(Tag('Series %s'%random_string(1), parent_tag))
    
    transaction.commit()
    
    
    # --------------------------------------------------------------------------
    
    tags = DBSession.query(Tag).all()
    
    def get_random_tags(num_tags=None):
        random_tags = []
        if not num_tags:
            num_tags = random.randint(1,5)
        for tag_num in range(num_tags):
            random_tags.append(tags[random.randint(0,len(tags)-1)])
        return random_tags
    
    def get_random_description(words=None, word_size=None):
        if not words:
            words     = random.randint(4,24)
        if not word_size:
            word_size = random.randint(2,16)
        return " ".join([random_string(word_size) for word in range(words)])
    
    
    # Track generation ---------------------------------------------------------
    for track_number in range(num_tracks):    
        track = Track()
        track.id          = "track_%d"      % track_number
        track.title       = "Test Track %s" % track_number
        track.description = get_random_description()
        track.duration    = random.randint(60,360)
        track.tags        = list(set(get_random_tags()))
        track.attachments = attachments
        DBSession.add(track)
    
    transaction.commit()
