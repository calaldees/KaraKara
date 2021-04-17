import json
from typing import Dict, Any

from pyramid.view import view_config

from . import action_ok, action_error

from karakara.model.model_tracks import Track, Attachment, _attachment_types
from karakara.model import DBSession, commit
from karakara.model.actions import get_tag, delete_track
ATTACHMENT_TYPES = set(_attachment_types.enums)

import logging
log = logging.getLogger(__name__)


def _get_json_request(request) -> Any:
    try:
        return request.json
    except json.JSONDecodeError:
        raise action_error('required json track data to import', code=400)


def _existing_tracks_dict() -> Dict[str, str]:
    return {t.id: t.source_filename for t in DBSession.query(Track.id, Track.source_filename)}


@view_config(
    context='karakara.traversal.TrackImportContext',
    request_method='GET',
)
def tracks(request):
    return action_ok(data={
        'tracks': _existing_tracks_dict()
    })


@view_config(
    context='karakara.traversal.TrackImportContext',
    request_method='POST',
)
def track_import_post(request):
    existing_track_ids = _existing_tracks_dict().keys()

    for track_dict in _get_json_request(request):
        if track_dict['id'] in existing_track_ids:
            log.warning(f"Exists: {track_dict['source_filename']} - {track_dict['id']}")
            continue

        log.info(f"Import: {track_dict['source_filename']} - {track_dict['id']}")
        track = Track()
        track.id = track_dict['id']
        track.source_filename = track_dict['source_filename']
        track.duration = track_dict['duration']
        track.srt = track_dict['srt']

        # Attachments
        for attachment_dict in track_dict['attachments']:
            assert attachment_dict['type'] in ATTACHMENT_TYPES
            attachment = Attachment()
            attachment.type = attachment_dict['type']
            attachment.location = attachment_dict['location']
            track.attachments.append(attachment)

        # Tags
        for tag_string in track_dict['tags']:
            tag = get_tag(tag_string, create_if_missing=True)
            if tag:
                track.tags.append(tag)
            elif tag_string:
                log.warning('null tag %s', tag_string)
        for duplicate_tag in (tag for tag in track.tags if track.tags.count(tag) > 1):
            log.warning('Unneeded duplicate tag found %s in %s', duplicate_tag, track.source_filename)
            track.tags.remove(duplicate_tag)

        DBSession.add(track)
        commit()

    request.registry.settings['karakara.tracks.version'] += 1
    return action_ok()


@view_config(
    context='karakara.traversal.TrackImportContext',
    request_method='DELETE',
)
def track_delete(request):
    existing_track_ids = _existing_tracks_dict().keys()
    for track_id in _get_json_request(request):
        if track_id in existing_track_ids:
            delete_track(track_id)
            request.registry.settings['karakara.tracks.version'] += 1
            log.info(f'Delete: {track_id}')
        else:
            log.warning(f'NotExists: {track_id}')
    return action_ok()
