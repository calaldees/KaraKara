from pyramid.view import view_config

from . import web

from ..lib.misc        import update_dict
from ..lib.auto_format import action_ok, registered_formats

from ..model              import DBSession
from ..model.model_tracks import Track, Tag, TrackTagMapping
from ..model.actions      import get_tag

import re
from sqlalchemy.orm import joinedload
from sqlalchemy     import func


@view_config(route_name='tags')
@web
def tags(request):
    # Hack - remove any format tags from route match - idealy this would be done at the route level
    url  = re.sub('|'.join(['\.'+f for f in registered_formats()]),'',request.matchdict['tags'])
    
    try   : tags     = url.split('/')
    except: tags     = []
    try   : keywords = request.params['keywords'].split(' ')
    except: keywords = []
    
    # Transform tag strings into tag objects # This involkes a query for each tag ... a small overhead
    #  any tags that dont match are added as keywords
    tag_objs = []
    for tag in tags:
        tag_obj = get_tag(tag)
        if tag_obj:
            tag_objs.append(tag_obj)
        else:
            keywords.append(tag)
    tags = tag_objs
    
    trackids = DBSession.query(Track.id)
    for tag in tags:
        trackids = trackids.intersect( DBSession.query(Track.id).join(Track.tags).filter(Tag.id              == tag.id  ) )
    for keyword in keywords:
        trackids = trackids.intersect( DBSession.query(Track.id).join(Track.tags).filter(Tag.name.like('%%%s%%' % keyword)) )
    
    return action_ok(
        data={
            'tags'    : [str(tag) for tag in tags],
            'keywords': keywords,
            'trackids': [trackid[0] for trackid in trackids.all()],
        }
    )

def tags_old():
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
    
    # Don't return tracks if there are too many returns, force the user to select more subtags
    if tracks.count() > 10:
        tracks = []
    
    return action_ok(
        data={
            'tracks'  : [track.to_dict('full') for track in tracks],
            'sub_tags': [update_dict(tag.to_dict(),{'count':count})   for tag,count in sub_tags if tag not in tags],
            'tags'    : tag_strings,
        }
    )
