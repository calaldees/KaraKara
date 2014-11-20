import os
import random
import re
import json
import shutil

from pyramid.view import view_config
from pyramid.events import subscriber

from sqlalchemy.orm import joinedload

from externals.lib.misc import backup
from externals.lib.pyramid_helpers import get_setting
from externals.lib.pyramid_helpers.views.upload import EventFileUploaded

from ..model import DBSession
from ..model.model_tracks import Track

from . import web, action_ok, cache, etag_decorator, generate_cache_key, comunity_only, is_comunity  # action_error,

from ..scripts.import_tracks import import_json_data as import_track
from ..views.tracks import invalidate_track
from ..templates import helpers as h

import logging
log = logging.getLogger(__name__)


#-------------------------------------------------------------------------------
# Cache Management
#-------------------------------------------------------------------------------
LIST_CACHE_KEY = 'comunity_list'

list_version = random.randint(0, 2000000000)
def invalidate_list_cache(request=None):
    global list_version
    list_version += 1
    cache.delete(LIST_CACHE_KEY)


def _generate_cache_key_comunity_list(request):
    global list_version
    return '-'.join([generate_cache_key(request), str(list_version), str(is_comunity(request))])


#-------------------------------------------------------------------------------
# Events
#-------------------------------------------------------------------------------

@subscriber(EventFileUploaded)
def file_uploaded(event):
    upload_path = get_setting('upload.path')
    media_path = get_setting('static.media')

    # Move uploaded files into media path
    uploaded_files = (f for f in os.listdir(upload_path) if os.path.isfile(os.path.join(upload_path, f)))
    for f in uploaded_files:
        shutil.move(
            os.path.join(upload_path, f),
            os.path.join(media_path, f),
        )

    invalidate_list_cache()


#-------------------------------------------------------------------------------
# Community Utils
#-------------------------------------------------------------------------------

class ComunityTrack():
    """
    Tracks are more than just a db entry. They have static data files accociated
    with them.
    These static data files are used to import tracks into the db.
    Rather than just changing our own local db, we need to update modify and manage
    these external static files.

    ComunityTrack is an object that wraps a Track with additional methods to
    manipulate these files.
    """
    _open = open

    @classmethod
    def factory(cls, track_id, request):
        return ComunityTrack(track_id, request.registry.settings['static.media'], open=cls._open)

    def __init__(self, track_id, media_path, open=open):
        assert track_id and track_id != 'undefined', 'track_id required'
        assert media_path
        self.media_path = media_path
        self.track_id = track_id
        self._track_dict = None
        self._import_required = False
        self._open = open  # Allow mockable open() for testing

    @property
    def track(self):
        if not self._track_dict:
            self._track_dict = DBSession.query(Track) \
                .options( \
                    joinedload(Track.tags), \
                    joinedload(Track.attachments), \
                    joinedload('tags.parent'), \
                    joinedload('lyrics'), \
                ) \
                .get(self.track_id).to_dict('full')
        return self._track_dict

    def import_track(self):
        with self._open(self.path_description_filename, 'r') as filehandle:
            import_track(filehandle, self.path_description_filename)
            invalidate_track(self.track_id)

    @property
    def path(self):
        return os.path.join(self.media_path, self.track['source_filename'])

    @property
    def path_backup(self):
        return os.path.join(self.path, '_old_versions')

    @property
    def path_source(self):
        return os.path.join(self.path, 'source')

    @property
    def path_description_filename(self):
        return os.path.join(self.path, 'description.json')

    @property
    def tag_data_filename(self):
        return os.path.join(self.path, 'tags.txt')

    @property
    def tag_data_raw(self):
        with self._open(self.tag_data_filename, 'r') as tag_data_filehandle:
            return tag_data_filehandle.read()
    @tag_data_raw.setter
    def tag_data_raw(self, tag_data):
        backup(self.tag_data_filename, self.path_backup)
        with self._open(self.tag_data_filename, 'w') as filehandle:
            filehandle.write(tag_data)
            self._import_required = True

    @property
    def tag_data(self):
        return {tuple(line.split(':')) for line in self.tag_data_raw.split('\n')}

    @property
    def source_data_filename(self):
        return os.path.join(self.path, 'sources.json')

    @property
    def source_data(self):
        with self._open(self.source_data_filename, 'r') as source_data_filehandle:
            return json.loads(source_data_filehandle.read())

    @property
    def subtitle_filenames(self):
        return [k for k in self.source_data.keys() if re.match(r'^.*\.(ssa|srt)$', k)]

    @property
    def subtitle_data(self):
        def subtitles_read(subtitle_filename):
            subtitle_filename = os.path.join(self.path_source, subtitle_filename)
            with self._open(subtitle_filename, 'r') as subtitle_filehandle:
                try:
                    return subtitle_filehandle.read()
                except UnicodeDecodeError:
                    # Temp fix - this needs to be resolved properly, this should perform it's 'best attempt' at decoding rather than crash
                    log.error('UnicodeDecodeError: {}'.format(subtitle_filename))
                    return 'UnicodeDecodeError'
        return dict(((subtitle_filename, subtitles_read(subtitle_filename)) for subtitle_filename in self.subtitle_filenames))
    @subtitle_data.setter
    def subtitle_data(self, subtitle_data):
        for subtitle_filename, subtitle_data_raw in subtitle_data:
            subtitle_path_filename = os.path.join(self.path_source, subtitle_filename)
            backup(subtitle_path_filename, self.path_backup)
            with self._open(subtitle_path_filename, 'w') as filehandle:
                filehandle.write(subtitle_data_raw)
                self._import_required = True

    @property
    def video_previews(self):
        return h.previews(self.track)


#-------------------------------------------------------------------------------
# Community Views
#-------------------------------------------------------------------------------

@view_config(route_name='comunity')
@web
def comunity(request):
    return action_ok()


@view_config(route_name='comunity_upload')
@web
def comunity_upload(request):
    return action_ok()


@view_config(route_name='comunity_list')
@etag_decorator(_generate_cache_key_comunity_list)
@web
@comunity_only
def comunity_list(request):

    def _comnunity_list():
        # Get tracks from db
        tracks = [
            track.to_dict('full', exclude_fields=('lyrics','attachments','image')) \
            for track in DBSession.query(Track) \
                .order_by(Track.source_filename) \
                .options( \
                    joinedload(Track.tags), \
                    #joinedload(Track.attachments), \
                    joinedload('tags.parent'), \
                    #joinedload('lyrics'), \
                )
        ]

        # Get track folders from media source
        media_path = request.registry.settings['static.media']
        media_folders, unprocessed_media_files = set(), set()
        if os.path.isdir(media_path):
            media_folders = set(folder for folder in os.listdir(media_path) if os.path.isdir(os.path.join(media_path, folder)))
            unprocessed_media_files = set(f for f in os.listdir(media_path) if os.path.isfile(os.path.join(media_path, f)) and not f.startswith('.'))

        # Compare folder sets to identify unimported/renamed files
        track_folders = set((track['source_filename'] for track in tracks))
        not_imported = media_folders.difference(track_folders)
        missing_source = track_folders.difference(media_folders)

        return {
            'tracks': tracks,
            'unprocessed_media_files': sorted(unprocessed_media_files),
            'not_imported': sorted(not_imported),
            'missing_source': sorted(missing_source),
        }

    data_tracks = cache.get_or_create(LIST_CACHE_KEY, _comnunity_list)
    return action_ok(data=data_tracks)


@view_config(route_name='comunity_track', request_method='GET')
@web
@comunity_only
def comunity_track(request):
    id = request.matchdict['id']
    log.debug('comunity_track {}'.format(id))
    ctrack = ComunityTrack.factory(id, request)
    return action_ok(data={
        'track': ctrack.track,
        'tag_matrix': {},
        'tag_data': ctrack.tag_data_raw,
        'subtitles': ctrack.subtitle_data,
        'previews': ctrack.video_previews,
    })
    # Todo - should throw action error with details on fail. i.e. if static files unavalable


@view_config(route_name='comunity_track', request_method='POST')
@web
@comunity_only
def comunity_track_update(request):
    id = request.matchdict['id']
    log.debug('comunity_track_update {}'.format(id))
    ctrack = ComunityTrack.factory(id, request)
    # Save tag data
    if 'tag_data' in request.params:
        ctrack.tag_data_raw = request.params['tag_data']

    # rebuild subtitle_data dict
    subtitle_data = {(k.replace('subtitles_', ''), v) for k, v in request.params.items() if k.startswith('subtitles_')}
    if subtitle_data:
        ctrack.subtitle_data = subtitle_data

    if ctrack._import_required:
        ctrack.import_track()

    return action_ok()
