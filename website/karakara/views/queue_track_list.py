from pyramid.view import view_config

from sqlalchemy.orm import joinedload

from . import web, action_ok, action_error, etag_decorator, cache, cache_none, generate_cache_key, admin_only
from .queue_search import _restrict_search

from ..model import DBSession
from ..model.model_tracks import Track

from ..templates.helpers import tag_hireachy

import logging
log = logging.getLogger(__name__)


#@view_config(route_name='track_list')
#@etag(tracks_etag)
#@web
#def track_list(request):
#    """
#    Browse tracks
#    """
#    #track_list = []
#    #for track in DBSession.query(Track).all():
#    #    track_list.append(track.id)
#    return action_ok(data={'list':[track.to_dict() for track in DBSession.query(Track).all()]})


#def track_list_cache_key(request):
#    '{0}-{1}-{2}'.format(
#        generate_cache_key(request),
#        request.registry.settings.get('karakara.search.tag.silent_forced', []),
#        request.registry.settings.get('karakara.search.tag.silent_hidden', []),
#    )



@view_config(
    context='karakara.traversal.TrackListContext'
    # TODO: get_cache_bucket_function cache_key
)
#@etag_decorator(track_list_cache_key)
#@web
@admin_only
def track_list_all(request):
    """
    Return a list of every track in the system (typically for printing)
    """
    log.info('track_list')

    tracks = _restrict_search(
        DBSession.query(Track).options(
            joinedload(Track.tags),
            joinedload('tags.parent'),
            #defer(Track.lyrics),
        ),
        request.queue.settings.get('karakara.search.tag.silent_forced', []),
        request.queue.settings.get('karakara.search.tag.silent_hidden', []),
        obj_intersect=Track,
    )
    track_list = [track.to_dict(include_fields='tags') for track in tracks]

    # The id is very long and not sutable for a printed list.
    # We derive a truncated id specially for this printed list
    short_id_length = request.queue.settings.get('karakara.print_tracks.short_id_length', 6)
    for track in track_list:
        track['id_short'] = track['id'][:short_id_length]

    # Sort track list
    #  this needs to be handled at the python layer because the tag logic is fairly compicated
    fields = request.queue.settings.get('karakara.print_tracks.fields', [])
    def key_track(track):
        return " ".join([tag_hireachy(track['tags'], field) for field in fields])
    track_list = sorted(track_list, key=key_track)

    return action_ok(data={'list': track_list})
