from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from . import web

from ..lib.misc        import update_dict
from ..lib.auto_format import action_ok, registered_formats

from ..model              import DBSession
from ..model.model_tracks import Track, Tag, TrackTagMapping
from ..model.actions      import get_tag
from ..templates.helpers  import search_url, track_url

import re
import copy
from sqlalchemy     import func
from sqlalchemy.sql import null
from sqlalchemy.orm import joinedload, aliased


#-------------------------------------------------------------------------------
# Constants
tag_cats = {
    'root'           : ['category','vocalstyle','vocaltrack','lang'],
    'category:anime' : ['from'],
    'category:jdrama': ['from'],
    'category:game'  : ['from'],
    'category:jpop'  : ['artist','from'],

}

#-------------------------------------------------------------------------------

def search(request):
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
        elif tag:
            keywords.append(tag)
    tags = tag_objs
    
    # Get trackids for all tracks that match the tags and keywords
    trackids = DBSession.query(Track.id)
    for tag in tags:
        trackids = trackids.intersect( DBSession.query(Track.id).join(Track.tags).filter(Tag.id                == tag.id  ) )
    for keyword in keywords:
        trackids = trackids.intersect( DBSession.query(Track.id).join(Track.tags).filter(Tag.name.like('%%%s%%' % keyword)) )
    
    # Limit sub tag categorys for last tag selected
    #    and remove any selection of previous tags with the same parent
    try   : sub_tags_allowed = copy.copy(tag_cats[str(tags[-1])])
    except: sub_tags_allowed = copy.copy(tag_cats['root'])
    for tag in tags:
        try   : sub_tags_allowed.remove(tag.parent.name)
        except: pass
    
    return action_ok(
        data={
            'tags'    : [str(tag) for tag in tags],
            'keywords': keywords,
            'trackids': [trackid[0] for trackid in trackids.all()],
            'sub_tags_allowed': sub_tags_allowed,
        }
    )
    

@view_config(route_name='search_tags')
@web
def tags(request):
    action_return = search(request)

    tags             = action_return['data']['tags']
    keywords         = action_return['data']['keywords']
    sub_tags_allowed = action_return['data']['sub_tags_allowed']
    trackids         = action_return['data']['trackids']
    
    # If html request then we want to streamline browsing and remove redundent extra steps to get to the track list or track
    if request.matchdict['format']=='html':
        if len(trackids)==1:
            raise HTTPFound(location=track_url(trackids[0]))
        if len(trackids)<10:
            raise HTTPFound(location=search_url(tags,keywords,'search_list'))
    
    # Get a list of all the tags for all the trackids
    # Group them by tag name
    # only allow tags in the allowed list (there could be 100's of title's and from's), we just want the browsable ones
    alias_parent_tag = aliased(Tag)
    sub_tags = DBSession.query(Tag  ,func.count(TrackTagMapping.tag_id)).\
                        join(TrackTagMapping).\
                        join(alias_parent_tag, Tag.parent).\
                        filter(TrackTagMapping.track_id.in_(trackids)).\
                        filter(alias_parent_tag.name.in_(sub_tags_allowed)).\
                        group_by(Tag.id).\
                        order_by(alias_parent_tag.name,Tag.name).\
                        options(joinedload(Tag.parent))
    
    action_return['data'].update({
        'sub_tags': [update_dict(tag.to_dict('full'),{'count':count}) for tag,count in sub_tags], # if tag not in tags
    })
    return action_return


@view_config(route_name='search_list')
@web
def list(request):
    action_return = search(request)

    trackids = action_return['data']['trackids']

    tracks   = DBSession.query(Track).\
                        filter(Track.id.in_(trackids)).\
                        options(\
                            joinedload(Track.tags),\
                            joinedload(Track.attachments),\
                            joinedload('tags.parent'),\
                        )
    
    action_return['data'].update({
        'tracks'  : [track.to_dict('full', exclude_fields='lyrics') for track in tracks],
    })
    return action_return

