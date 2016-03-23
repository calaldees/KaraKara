import pytest
import random

from sqlalchemy.orm import aliased, joinedload

#from ..model import DBSession, commit
from externals.lib.misc import random_string

from karakara.model.actions import get_tag
from karakara.model.model_tracks import Track, Tag, Attachment
#from karakara.model.model_queue  import QueueItem

import logging
log = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def random_tracks(request, DBSession, commit, num_tracks=800):
    """
    Generate 100's of random tracks
    """
    log.info('Generating {0} random tracks'.format(num_tracks))

    # Attachment generation ----------------------------------------------------
    attachments_meta = [
        ('preview1.3gp', 'preview'),
        ('preview2.flv', 'preview'),
        ('image1.jpg', 'image'),
        ('image2.jpg', 'image'),
        ('image3.png', 'image'),
        ('processed.mpg', 'video'),
        ('subtitles.srt', 'srt'),
    ]
    attachments = []
    for location, type in attachments_meta:
        attachment = Attachment()
        attachment.location = location
        attachment.type     = type
        DBSession.add(attachment)
        attachments.append(attachment)
    commit()
    
    # Random Tag generation ----------------------------------------------------
    parent_tag = get_tag('from')
    for series_num in range(10):
        DBSession.add(Tag('Series %s'%random_string(1), parent_tag))
    commit()
    
    
    # --------------------------------------------------------------------------
    
    tags = DBSession.query(Tag).options(joinedload(Tag.parent)).all()
    alias_parent_tag = aliased(Tag)
    tags_category = DBSession.query(Tag).join(alias_parent_tag, Tag.parent).filter(alias_parent_tag.name=='category').all()
    tags_from     = DBSession.query(Tag).join(alias_parent_tag, Tag.parent).filter(alias_parent_tag.name=='from').all()
    
    def get_random_tags(num_tags=None):
        random_tags = []
        if not num_tags:
            num_tags = random.randint(1,5)
        for tag_num in range(num_tags):
            random_tags.append(tags[random.randint(0,len(tags)-1)])
        
        # if we have 'from' tags and NO category tag, then add a random category
        from_tags = [t for t in random_tags if t.parent and t.parent.name=='from']
        category_tags = [t for t in random_tags if t.parent and t.parent.name=='category']
        if from_tags and not category_tags:
            random_tags.append(random.choice(tags_category))
        if category_tags and not from_tags:
            random_tags.append(random.choice(tags_from))
        # only have 1 'from' tag
        for tag in from_tags[1:]:
            random_tags.remove(tag)
        # only have one category tag
        for tag in category_tags[1:]:
            random_tags.remove(tag)
        
        return random_tags
    
    def get_random_description(words=None, word_size=None):
        if not words:
            words     = random.randint(4,24)
        if not word_size:
            word_size = random.randint(2,16)
        return " ".join([random_string(word_size) for word in range(words)])
        
    # Track generation ---------------------------------------------------------
    tag_titles = [get_tag('Test Track {0}'.format(i), 'title', create_if_missing=True) for i in range(num_tracks)]
    #commit()

    for track_number in range(num_tracks):
        track = Track()
        track.id          = "track_%d"      % track_number
        #track.description = get_random_description()
        track.duration    = random.randint(60,360)
        track.tags        = list(set(get_random_tags())) + [tag_titles[track_number]]
        track.attachments = attachments
        DBSession.add(track)
    
    commit()
