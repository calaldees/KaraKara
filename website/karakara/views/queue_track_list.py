from pyramid.view import view_config
import srt

from sqlalchemy.orm import joinedload, undefer

from . import web, action_ok, action_error, etag_decorator, generate_cache_key, admin_only
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

def acquire_cache_bucket_func(request):
    request.log_event()
    return request.cache_manager.get(
        '-'.join(map(str, {
            'context_name': request.context.__name__,
            'queue_id': request.context.queue_id,
            'track_version': request.registry.settings['karakara.tracks.version'],
            'tag.silent_forced': request.registry.settings.get('karakara.search.tag.silent_forced', []),
            'tag.silent_hidden': request.registry.settings.get('karakara.search.tag.silent_hidden', []),
        }.values()))
    )


@view_config(
    context='karakara.traversal.TrackListContext',
    acquire_cache_bucket_func=acquire_cache_bucket_func,
)
def track_list_all(request):
    """
    Return a list of every track in the system (typically for printing)
    """
    log.info('track_list')

    tracks = _restrict_search(
        DBSession.query(Track),
        request.queue.settings.get('karakara.search.tag.silent_forced', []),
        request.queue.settings.get('karakara.search.tag.silent_hidden', []),
        obj_intersect=Track,
    ).options(
        joinedload(Track.attachments),
        joinedload(Track.tags),
        joinedload('tags.parent'),
        undefer(Track.srt),
    )
    track_list = [track.to_dict(include_fields=('tags', 'attachments', 'srt')) for track in tracks]

    # The id is very long and not suitable for a printed list.
    # We derive a truncated id specially for this printed list
    short_id_length = request.queue.settings.get('karakara.print_tracks.short_id_length', 6)

    # Hack/Patch for title of tracks
    # Browser2 does this on the client-side - can be removed if we remove
    # server-side track browsing
    for track in track_list:
        track['id_short'] = track['id'][:short_id_length]
        if track['tags'].get('vocaltrack') == ["off"]:
            track['title'] += " (Karaoke Ver)"

        # Convert SRT format lyrics in 'srt' property
        # into JSON format lyrics in 'lyrics' property
        try:
            if track['srt']:
                track['lyrics'] = [{
                    'id': line.index,
                    'text': line.content,
                    'start': line.start.total_seconds(),
                    'end': line.start.total_seconds(),
                } for line in srt.parse(track['srt'])]
        except Exception as e:
            log.exception(f"Error parsing subtitles for track {track['id']}")
        if 'lyrics' not in track:
            track['lyrics'] = []
        del track['srt']

    # Sort track list
    #  this needs to be handled at the python layer because the tag logic is fairly compicated
    fields = request.queue.settings.get('karakara.print_tracks.fields', [])
    def key_track(track):
        return " ".join([tag_hireachy(track['tags'], field) for field in fields])
    track_list = sorted(track_list, key=key_track)

    return action_ok(data={'list': track_list})
