from pyramid.view import view_config

from ..lib.misc        import update_dict
from ..lib.auto_format import auto_format_output, action_ok, registered_formats

from ..model              import DBSession
from ..model.model_tracks import Track, Tag, TrackTagMapping

import re
from sqlalchemy.orm import joinedload
from sqlalchemy     import func


@view_config(route_name='tags')
@auto_format_output
def tags(request):
    # Hack - remove any format tags from route match - idealy this would be done at the route level
    request.matchdict['tags'] = re.sub('|'.join(['\.'+f for f in registered_formats()]),'',request.matchdict['tags'])
    
    tag_strings = request.matchdict['tags'].split('/')
    
    #tags_single  = []
    #tags_parents = []
    #for tag in tag_strings:
    #    tag, tag_parent = tuple(tag.split(':'))
    #    if tag and tag_parent:
    #tracks = DBSession.query(Track).join(Track.tags).filter(Tag.id.in_([tag.id for tag in tags])).all()
    
    tags = DBSession.query(Tag).filter(Tag.name.in_(tag_strings))
    
    trackids = DBSession.query(Track.id)
    for tag in tags:
        trackids = trackids.intersect( DBSession.query(Track.id).join(Track.tags).filter(Tag.id==tag.id) )
    
    tracks   = DBSession.query(Track).filter(Track.id.in_(trackids)).options(joinedload(Track.tags),joinedload(Track.attachments))
    sub_tags = DBSession.query(Tag  ,func.count(TrackTagMapping.tag_id)).join(TrackTagMapping).filter(TrackTagMapping.track_id.in_(trackids)).group_by(Tag.id).options(joinedload(Tag.parent))
    
    return action_ok(
        data={
            'tracks'  : [track.to_dict('full') for track in tracks],
            'sub_tags': [update_dict(tag.to_dict(),{'count':count})   for tag,count in sub_tags],
        }
    )
