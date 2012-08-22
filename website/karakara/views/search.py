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

# A list of the sub tags allowed when browsing by specific tags
# rather than overwelming the user with all possible tags, limit the browsing to a subset under known circumstances.
tag_cats = {
    'root'           : ['category','vocalstyle','vocaltrack','lang'],
    'category:anime' : ['from'],
    'category:jdrama': ['from'],
    'category:game'  : ['from'],
    'category:jpop'  : ['artist','from'],
}

#-------------------------------------------------------------------------------

def search(request):
    """
    The base call for API methods 'list' and 'tags'
    
    Uses URL, Query string and form input to query trackdb for trackid's that match tags and keyworkds
    
    returns action_ok dict
        - that is overlalyed by additional query data by 'list' and 'tags' API calls
        
        data {
            tags     - tags involved in this query
            keywords - keywords involved in this query
            trackids - of all tracks returned by the tag/keyword search (used by calling methods querys)
            sub_tags_allowed - a list of tags that will be displayed for the next query (differnt catagorys may have differnt browsing patterns)
        }
    """
    # Hack - remove any format tags from route match - idealy this would be done at the route level
    url  = re.sub('|'.join(['\.'+f for f in registered_formats()]),'',request.matchdict['tags'])
    
    try   : tags     = url.split('/')
    except: tags     = []
    try   : keywords = [keyword for keyword in re.findall(r'\w+', request.params['keywords']) if keyword]
    except: keywords = []
    try   : trackids = [trackid for trackid in re.findall(r'\w+', request.params['trackids']) if trackid]
    except: trackids = []
    
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
    
    # If trackids not manually given in request - Get trackids for all tracks that match the tags and keywords
    if not trackids:
        trackids = DBSession.query(Track.id)
        for tag in tags:
            trackids = trackids.intersect( DBSession.query(Track.id).join(Track.tags).filter(Tag.id                == tag.id  ) )
        for keyword in keywords:
            trackids = trackids.intersect( DBSession.query(Track.id).join(Track.tags).filter(Tag.name.like('%%%s%%' % keyword)) )
        trackids = [trackid[0] for trackid in trackids.all()]
    
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
            'trackids': trackids,
            'sub_tags_allowed': sub_tags_allowed,
        }
    )
    

@view_config(route_name='search_tags')
@web
def tags(request):
    """
    Browse tacks by 'tag'
    
    if there is only one track then redirect to show the single track
    if the number of tracks being browsed is less then 15 then redirect to 'list'
    
    Get all tags from all the tracks trackid's provided and count the number of occurances.
    
    return search dict + sub_tags( a list of all tags with counts )
    """
    action_return = search(request)

    tags             = action_return['data']['tags']
    keywords         = action_return['data']['keywords']
    sub_tags_allowed = action_return['data']['sub_tags_allowed']
    trackids         = action_return['data']['trackids']
    
    # If html request then we want to streamline browsing and remove redundent extra steps to get to the track list or track

    
    if request.matchdict['format']=='html':
        # If there is only one track present - abort and redirect to single track view, there is no point in doing any more work
        if len(trackids)== 1:
            raise HTTPFound(location=track_url(trackids[0]))
        # If there is only a small list, we might as well just show them all
        if len(trackids)< 15:
            raise HTTPFound(location=search_url(tags=tags,keywords=keywords,route='search_list'))
    
    # Get a list of all the tags for all the trackids
    # Group them by tag name
    # only allow tags in the allowed list (there could be 100's of title's and from's), we just want the browsable ones
    alias_parent_tag = aliased(Tag)
    sub_tags = DBSession.query(Tag  ,func.count(TrackTagMapping.tag_id)).\
                        join(TrackTagMapping).\
                        join(alias_parent_tag, Tag.parent).\
                        filter(TrackTagMapping.track_id.in_(trackids)).\
                        filter(alias_parent_tag.name.in_(sub_tags_allowed)).\
                        group_by('tag_1.id',alias_parent_tag.name,Tag.id).\
                        order_by(alias_parent_tag.name,Tag.name).\
                        options(joinedload(Tag.parent))
    
    # AllanC - RRRRRRRAAAAAAAAA!!!! Postgres creates an alias 'tag_1.id' under the hood, but wont actually return results unless it's in the group_by clause
    #          it works without the tag_1.id in sqllite. So right now, the SQLLite version is broken with 'tag_1' and postgres dies without it.
    #          is there a way to alias this properly?
    # tried alias's 'tag_1.id','tag_2.name'
    
    action_return['data'].update({
        'sub_tags': [update_dict(tag.to_dict('full'),{'count':count}) for tag,count in sub_tags],
    })
    return action_return


@view_config(route_name='search_list')
@web
def list(request):
    """
    Browse tacks by 'list'
    
    List all the tracks listed in trackids
    
    return search dict (see above) + tracks (a list of tracks with basic details)
    """

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
        'tracks'  : [track.to_dict('full', exclude_fields='lyrics,attachments') for track in tracks],
    })
    return action_return

