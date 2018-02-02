import re
import copy
import random
import collections

from sqlalchemy import func
from sqlalchemy.orm import joinedload, aliased, defer

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.traversal import resource_path

from externals.lib.misc import update_dict
#from externals.lib.pyramid_helpers.auto_format import registered_formats

from . import web, cache, etag, action_ok, cache_manager # generate_cache_key,

from ..model import DBSession
from ..model.model_tracks import Track, Tag, TrackTagMapping
from ..model.actions import get_tag
#from ..templates.helpers import search_url, track_url

import logging
log = logging.getLogger(__name__)



# A list of the sub tags allowed when browsing by specific tags
# rather than overwelming the user with all possible tags, limit the browsing to a subset under known circumstances.
search_config = {}

# Utils ------------------------------------------------------------------------

def acquire_cache_bucket_func(request):
    search_params = _get_search_params_from_request(request)
    request.log_event(tags=search_params.tags, keywords=search_params.keywords)
    return cache_manager.get(
        '-'.join(map(str, {
            'context_name': request.context.__name__,
            'queue_id': request.context.queue_id,
            'track_version': request.registry.settings['karakara.tracks.version'],
            **search_params._asdict(),
        }.values()))
    )


def response_callback_search_max_age(request, response):
    """
    Set the cache_control max_age for the response
    Use with:
        request.add_response_callback(response_callback_search_max_age)
    """
    if request.exception is not None:
        response.cache_control.max_age = request.registry.settings.get('api.search.max_age')


SearchParams = collections.namedtuple('SearchParams', ('tags', 'keywords', 'trackids', 'tags_silent_forced', 'tags_silent_hidden', 'version'))

REGEX_SPLIT_QUERY_STRING = re.compile(r'[^ ,]+')

def _get_search_params_from_request(request):
    def parse_query_string_key(key):
        return REGEX_SPLIT_QUERY_STRING.findall(request.params.get(key, ''))
    return SearchParams(
        tags=tuple(request.context.tags),
        keywords=tuple(sorted(parse_query_string_key('keywords'))),
        trackids=tuple(parse_query_string_key('trackids')),
        tags_silent_forced=tuple(request.queue.settings.get('karakara.search.tag.silent_forced', [])),
        tags_silent_hidden=tuple(request.queue.settings.get('karakara.search.tag.silent_hidden', [])),
        version=request.registry.settings['karakara.tracks.version'],
    )


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
    return tag_objs, tuple(tag_unknown)


def _restrict_search(query, tags_silent_forced, tags_silent_hidden, obj_intersect=Track.id):
    """
    Attempted to extract out track restriction but ended up with a mess.
    passing differnt obj_intersects is messy and unclear. Poo!
    """
    tags_silent_forced, _ = _tag_strings_to_tag_objs(tags_silent_forced)
    tags_silent_hidden, _ = _tag_strings_to_tag_objs(tags_silent_hidden)

    for tag in tags_silent_forced:
        query = query.intersect(DBSession.query(obj_intersect).join(Track.tags).filter(Tag.id == tag.id))
    for tag in tags_silent_hidden:
        query = query.filter(Track.id.notin_(DBSession.query(Track.id).join(Track.tags).filter(Tag.id == tag.id)))

    return query


#-------------------------------------------------------------------------------

@cache.cache_on_arguments()
def _search(search_params):
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
    tags, keywords, trackids, tags_silent_forced, tags_silent_hidden, version = search_params
    log.debug(f'cache gen - search - {tags} - {keywords} - {trackids}')

    # Any tags that are not part of our database are added as 'keywords' instead.
    tags, tag_unknown = _tag_strings_to_tag_objs(tags)
    keywords += tag_unknown

    # If trackids not manually given in request - Get trackids for all tracks that match the tags and keywords
    if not trackids:
        trackids = DBSession.query(Track.id)
        trackids = _restrict_search(trackids, tags_silent_forced, tags_silent_hidden)
        for tag in tags:
            trackids = trackids.intersect(DBSession.query(Track.id).join(Track.tags).filter(Tag.id == tag.id))
        for keyword in keywords:
            trackids = trackids.intersect(DBSession.query(Track.id).join(Track.tags).filter(Tag.name.like('%%%s%%' % keyword)) )

        trackids = [trackid[0] for trackid in trackids.all()]

    # Limit sub tag categorys for last tag selected
    #    and remove any selection of previous tags with the same parent
    try:
        sub_tags_allowed = copy.copy(search_config[str(tags[-1])])
    except Exception:
        sub_tags_allowed = copy.copy(search_config['root'])
    for tag in tags:
        try:
            sub_tags_allowed.remove(tag.parent.name)
        except Exception:
            pass

    return action_ok(
        data={
            'tags': [str(tag) for tag in tags],
            'keywords': keywords,
            'trackids': trackids,
            'sub_tags_allowed': sub_tags_allowed,
        }
    )


@view_config(
    context='karakara.traversal.SearchTagsContext',
    acquire_cache_bucket_func=acquire_cache_bucket_func,
)
def tags(request):
    """
    Browse tacks by 'tag'

    if there is only one track then redirect to show the single track
    if the number of tracks being browsed is less then 15 then redirect to 'list'

    Get all tags from all the tracks trackid's provided and count the number of occurances.

    return search dict + sub_tags( a list of all tags with counts )
    """
    request.add_response_callback(response_callback_search_max_age)

    action_return = _search(_get_search_params_from_request(request))

    tags             = action_return['data']['tags']
    keywords         = action_return['data']['keywords']
    sub_tags_allowed = action_return['data']['sub_tags_allowed']
    trackids         = action_return['data']['trackids']

    # If html request then we want to streamline browsing and remove redundent extra steps to get to the track list or track
    # TODO: I'm unsure if these 'raise' returns can be cached - right now this call always makes 2 hits to the cache search() and get_action_return_with_sub_tags()
    if request.requested_response_format == 'html':
        # If there is only one track present - abort and redirect to single track view, there is no point in doing any more work
        if len(trackids)== 1:
            # TODO if the hostname has a port, the port is stripped ... WTF?!
            raise HTTPFound(location=resource_path(request.context.queue_context['track'][trackids[0]]))
        # If there is only a small list, we might as well just show them all
        if len(trackids) < request.queue.settings['karakara.search.list.threshold']:
            # TODO: Lame - This url is created with string concatination. Use a proper builder.
            raise HTTPFound(location='{path}?keywords={keywords}'.format(
                path=resource_path(request.context.queue_context['search_list'], *tags),
                keywords=','.join(keywords),
            ))

    def get_action_return_with_sub_tags():
        log.debug('cache gen - subtags')
        # Get a list of all the tags for all the trackids
        # Group them by tag name
        # only allow tags in the allowed list (there could be 100's of title's and from's), we just want the browsable ones
        alias_parent_tag = aliased(Tag)

        # The SQL engine cannot cope with an 'IN' clause with over 1000 enties
        # The solution is a convoluted way of batching the requests up into chunks
        # of 1000 and merging the results

        def get_sub_tags_batch(trackids):

            def slice_batch(trackids, batch_size):
                for batch_number in range(0, (len(trackids)//batch_size)+1):
                    yield trackids[batch_number * batch_size:(batch_number + 1) * batch_size]

            tags = {}
            for trackids_batch in slice_batch(trackids, 900):
                for tag, count in get_sub_tags(trackids_batch):
                    tag_dict = tag.to_dict('full')
                    id = tag_dict['id']
                    tags.setdefault(id, tag_dict).setdefault('count', 0)
                    tags[id]['count'] += count
            return tags.values()

        def get_sub_tags(trackids):
            return DBSession.query(Tag,
                func.count(TrackTagMapping.tag_id)).\
                join(TrackTagMapping).\
                join(alias_parent_tag, Tag.parent).\
                filter(TrackTagMapping.track_id.in_(trackids)).\
                filter(alias_parent_tag.name.in_(sub_tags_allowed)).\
                group_by('tag_1.id', alias_parent_tag.name, Tag.id).\
                order_by(alias_parent_tag.name, Tag.name).\
                options(joinedload(Tag.parent)
            )

        # This if branch con probably be removed - we don't want differnt behaviour for differnt db engines
        #  TODO: need to check if postgres can actually handle this properly
        if request.registry.settings.get('sqlalchemy.url', '').startswith('sqlite'):
            sub_tags = [tag for tag in get_sub_tags_batch(trackids)]
        else:
            sub_tags = [update_dict(tag.to_dict('full'), {'count': count}) for tag, count in get_sub_tags(trackids)]

        # AllanC - RRRRRRRAAAAAAAAA!!!! Postgres creates an alias 'tag_1.id' under the hood, but wont actually return results unless it's in the group_by clause
        #          it works without the tag_1.id in sqllite. So right now, the SQLLite version is broken with 'tag_1' and postgres dies without it.
        #          is there a way to alias this properly?
        # tried alias's 'tag_1.id','tag_2.name'

        action_return['data'].update({
            'sub_tags': sub_tags,
        })
        return action_return

    return request.cache_bucket.get_or_create(get_action_return_with_sub_tags)


@view_config(
    context='karakara.traversal.SearchListContext',
    acquire_cache_bucket_func=acquire_cache_bucket_func,
)
def list(request):
    """
    Browse tacks by 'list'

    List all the tracks listed in trackids

    return search dict (see above) + tracks (a list of tracks with basic details)
    """
    request.add_response_callback(response_callback_search_max_age)

    def get_list():
        action_return = _search(_get_search_params_from_request(request))
        log.debug('cache gen - get_list')

        _trackids = action_return['data']['trackids']

        tracks = DBSession.query(Track).\
                            filter(Track.id.in_(_trackids)).\
                            options(\
                                joinedload(Track.tags),\
                                joinedload(Track.attachments),\
                                joinedload('tags.parent'),\
                                #defer(Track.lyrics),\
                            )

        action_return['data'].update({
            'tracks': [track.to_dict('full', exclude_fields='lyrics,attachments') for track in tracks],
        })
        return action_return

    return request.cache_bucket.get_or_create(get_list)
