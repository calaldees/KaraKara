from pyramid.view import view_config

from ..lib.auto_format import auto_format_output, action_ok, registered_formats

from ..model              import DBSession
from ..model.model_tracks import Track, Tag, TrackTagMapping

import re


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
    
    tags   = DBSession.query(Tag).filter(Tag.name.in_(tag_strings)).all()
    #tracks = DBSession.query(Track).join(Track.tags).filter(Tag.id.in_([tag.id for tag in tags])).all()
    
    tracks_with_tags = DBSession.query(Track)
    for tag in tags:
        tracks_with_tags = tracks_with_tags.intersect( DBSession.query(Track).join(Track.tags).filter(Tag.id==tag.id) )
    
    return action_ok(data={'tracks': [track.to_dict() for track in tracks_with_tags]})
