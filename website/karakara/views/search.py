import re
import copy
import random
import collections

from sqlalchemy     import func
#from sqlalchemy.sql import null
from sqlalchemy.orm import joinedload, aliased

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from externals.lib.misc import update_dict
from externals.lib.pyramid_helpers.auto_format import registered_formats

from . import web, cache, etag, action_ok, max_age   # generate_cache_key,

from ..model              import DBSession
from ..model.model_tracks import Track, Tag, TrackTagMapping
from ..model.actions      import get_tag
from ..templates.helpers  import search_url, track_url

import logging
log = logging.getLogger(__name__)


#-------------------------------------------------------------------------------
# Constants

search_version = random.randint(0,2000000000)

# A list of the sub tags allowed when browsing by specific tags
# rather than overwelming the user with all possible tags, limit the browsing to a subset under known circumstances.
search_config = {}

# Utils ------------------------------------------------------------------------

# cache control from settings
search_max_age = lambda request: request.registry.settings.get('api.search.max_age')

SearchParams = collections.namedtuple('SearchParams',['tags', 'keywords', 'trackids', 'tags_silent_forced', 'tags_silent_hidden'])

def get_search_params(request):
    # Hack - remove any format tags from route match - idealy this would be done at the route level
    url  = re.sub('|'.join(['\.'+f for f in registered_formats()]),'',request.matchdict['tags'])
    
    try   : tags     = url.split('/')
    except: tags     = []
    try   : keywords = sorted([keyword for keyword in re.findall(r'\w+', request.params['keywords']) if keyword])
    except: keywords = []
    try   : trackids = [trackid for trackid in re.findall(r'\w+', request.params['trackids']) if trackid]
    except: trackids = []

    tags_silent_forced = request.registry.settings.get('karakara.search.tag.silent_forced',[])
    tags_silent_hidden = request.registry.settings.get('karakara.search.tag.silent_hidden',[])

    return SearchParams(tags, keywords, trackids, tags_silent_forced, tags_silent_hidden)

def search_cache_key(search_params):
    return "{tags}-{keywords}-{trackids}-{tags_silent_forced}-{tags_silent_hidden}".format(**search_params._asdict())


def _tag_strings_to_tag_objs(tags):
    """
    Transform tag strings into tag objects
    This involkes a query for each tag ... a small overhead
    any tags that dont match are added as keywords
    """
    tag_objs = []
    tag_unknown = []
    for tag in tags:
        tag_obj = get_tag(tag)
        if tag_obj:
            tag_objs.append(tag_obj)
        elif tag:
            tag_unknown.append(tag)
    return tag_objs, tag_unknown

def restrict_search(request, query, obj_intersect=Track):
    return _restrict_search(
        query,
        request.registry.settings.get('karakara.search.tag.silent_forced',[]),
        request.registry.settings.get('karakara.search.tag.silent_hidden',[]),
        obj_intersect = obj_intersect,
    )

def _restrict_search(query, tags_silent_forced, tags_silent_hidden, obj_intersect=Track.id):
    """
    Attempted to extract out track restriction but ended up with a mess.
    passing differnt obj_intersects is messy and unclear. Poo!
    """
    tags_silent_forced, _ = _tag_strings_to_tag_objs(tags_silent_forced)
    tags_silent_hidden, _ = _tag_strings_to_tag_objs(tags_silent_hidden)

    for tag in tags_silent_forced:
        query = query.intersect(DBSession.query(obj_intersect).join(Track.tags).filter(Tag.id==tag.id))
    for tag in tags_silent_hidden:
        query = query.filter(Track.id.notin_(DBSession.query(obj_intersect).join(Track.tags).filter(Tag.id==tag.id)))

    return query

#-------------------------------------------------------------------------------

@cache.cache_on_arguments()
def search(search_params):
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
    tags, keywords, trackids, tags_silent_forced, tags_silent_hidden = search_params
    log.debug('cache gen - search {0}'.format(search_cache_key(search_params)))
    
    tags, tag_unknown = _tag_strings_to_tag_objs(tags)
    keywords += tag_unknown
    
    # If trackids not manually given in request - Get trackids for all tracks that match the tags and keywords
    if not trackids:
        trackids = DBSession.query(Track.id)
        trackids = _restrict_search(trackids, tags_silent_forced, tags_silent_hidden)
        for tag in tags:
            trackids = trackids.intersect( DBSession.query(Track.id).join(Track.tags).filter(Tag.id                == tag.id  ) )
        for keyword in keywords:
            trackids = trackids.intersect( DBSession.query(Track.id).join(Track.tags).filter(Tag.name.like('%%%s%%' % keyword)) )
        
        trackids = [trackid[0] for trackid in trackids.all()]

    # Limit sub tag categorys for last tag selected
    #    and remove any selection of previous tags with the same parent
    try   : sub_tags_allowed = copy.copy(search_config[str(tags[-1])])
    except: sub_tags_allowed = copy.copy(search_config['root'])
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
@max_age(search_max_age)
@web
def tags(request):
    """
    Browse tacks by 'tag'
    
    if there is only one track then redirect to show the single track
    if the number of tracks being browsed is less then 15 then redirect to 'list'
    
    Get all tags from all the tracks trackid's provided and count the number of occurances.
    
    return search dict + sub_tags( a list of all tags with counts )
    """
    search_params = get_search_params(request)
    cache_key = "search_tags_{0}:{1}".format(search_version, search_cache_key(search_params))
    etag(request, cache_key)  # Abort if 'etag' match
    
    action_return = search(search_params)

    tags             = action_return['data']['tags']
    keywords         = action_return['data']['keywords']
    sub_tags_allowed = action_return['data']['sub_tags_allowed']
    trackids         = action_return['data']['trackids']
    
    # If html request then we want to streamline browsing and remove redundent extra steps to get to the track list or track
    # TODO: I'm unsure if these 'raise' returns can be cached - right now this call always makes 2 hits to the cache search() and get_action_return_with_sub_tags()
    if request.matchdict['format']=='html':
        # If there is only one track present - abort and redirect to single track view, there is no point in doing any more work
        if len(trackids)== 1:
            # TODO if the hostname has a port, the port is stripped ... WTF?!
            raise HTTPFound(location=track_url(trackids[0]))
        # If there is only a small list, we might as well just show them all
        if len(trackids) < request.registry.settings['karakara.search.list.threshold']:
            raise HTTPFound(location=search_url(tags=tags,keywords=keywords,route='search_list'))
    
    def get_action_return_with_sub_tags():
        log.debug('cache gen - subtags')
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
    
    return cache.get_or_create(cache_key, get_action_return_with_sub_tags)


@view_config(route_name='search_list')
@max_age(search_max_age)
@web
def list(request):
    """
    Browse tacks by 'list'
    
    List all the tracks listed in trackids
    
    return search dict (see above) + tracks (a list of tracks with basic details)
    """
    search_params = get_search_params(request)
    cache_key = "search_list_{0}:{1}".format(search_version, search_cache_key(search_params))
    etag(request, cache_key)  # Abort if 'etag' match
    
    def get_list():
        action_return = search(search_params)
        log.debug('cache gen - get_list')
        
        _trackids = action_return['data']['trackids']
        
        tracks   = DBSession.query(Track).\
                            filter(Track.id.in_(_trackids)).\
                            options(\
                                joinedload(Track.tags),\
                                joinedload(Track.attachments),\
                                joinedload('tags.parent'),\
                            )
        
        action_return['data'].update({
            'tracks'  : [track.to_dict('full', exclude_fields='lyrics,attachments') for track in tracks],
        })
        return action_return
    
    return cache.get_or_create(cache_key, get_list)

