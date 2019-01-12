import os
import random
import re
import json
import shutil
from collections import defaultdict

from pyramid.view import view_config
from pyramid.events import subscriber

from sqlalchemy.orm import joinedload, undefer

from calaldees.data import first
from calaldees.files.backup import backup
from calaldees.pyramid_helpers import get_setting
from calaldees.pyramid_helpers.views.upload import EventFileUploaded

from ..model import DBSession
from ..model.model_tracks import Track

from . import action_ok, action_error, comunity_only, is_comunity

#from ..views.track import invalidate_track
from ..templates import helpers as h

import logging
log = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------

PATH_BACKUP_KEY = 'static.backup'
PATH_PROCESSMEDIA2_LOG = 'static.processmedia2.log'
PATH_UPLOAD_KEY = 'upload.path'

STATUS_TAGS = {
    'required': (),  # ('category', 'title'),
    'recommended': ('lang',),  # ('artist', ),
    'yellow': ('yellow', 'caution', 'warning', 'problem'),
    'red': ('red', 'broken', 'critical'),
    'black': ('black', 'delete', 'remove', 'deprecated'),
    'green': ('green', 'ok', 'checked')
}

STATUS_LIGHT_ORDER = ('black', 'green', 'red', 'yellow')


def get_overall_status(status_keys, status_light_order=STATUS_LIGHT_ORDER):
    for light in status_light_order:
        if light in status_keys:
            return light


#-------------------------------------------------------------------------------
# Cache Management
#-------------------------------------------------------------------------------
#LIST_CACHE_KEY = 'comunity_list'
#list_cache_timestamp = None

#list_version = random.randint(0, 2000000000)
#def invalidate_list_cache(request=None):
#    global list_version
#    list_version += 1
#    cache.delete(LIST_CACHE_KEY)
#
#def _generate_cache_key_comunity_list(request):
#    global list_version
#    return '-'.join([generate_cache_key(request), str(last_update()), str(list_version), str(is_comunity(request))])

def acquire_cache_bucket_func(request):
    try:
        _id = request.context.id
    except:
        _id = ''
    return request.cache_manager.get(f'comunity-{request.context.__name__}-{request.last_track_db_update}-{is_comunity(request)}-{_id}')



#-------------------------------------------------------------------------------
# Events
#-------------------------------------------------------------------------------

@subscriber(EventFileUploaded)
def file_uploaded(event):
    """
    Deprecated.
    Files are now updated from processmedia2.
    This can be removed.
    """
    upload_path = get_setting(PATH_UPLOAD_KEY)
    path_source = get_setting('static.path.source')

    # Move uploaded files into media path
    uploaded_files = (f for f in os.listdir(upload_path) if os.path.isfile(os.path.join(upload_path, f)))
    for f in uploaded_files:
        shutil.move(
            os.path.join(upload_path, f),
            os.path.join(path_source, f),
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
    def factory(cls, track, request):
        return ComunityTrack(
            track=track,
            path_source=request.registry.settings['static.path.source'],
            path_meta=request.registry.settings['static.path.meta'],
            path_backup=request.registry.settings[PATH_BACKUP_KEY],
            open=cls._open
        )

    def __init__(self, track, path_source, path_meta, path_backup, open=open):
        """
        Not to be called directly - use factory() instead
        """
        assert path_source
        assert path_backup
        assert path_meta
        self.path_source = path_source
        self.path_meta = path_meta
        self.path_backup = path_backup

        assert track, 'track required'
        if isinstance(track, str):
            assert track != 'undefined'
            self.track_id = track
            self._track_dict = None
        if isinstance(track, dict):
            self.track_id = track['id']
            self._track_dict = track

        self._open = open  # Allow mockable open() for testing

    @property
    def track(self):
        if not self._track_dict:
            self._track_dict = DBSession.query(Track).options(
                joinedload(Track.tags),
                joinedload(Track.attachments),
                joinedload('tags.parent'),
            ).get(self.track_id).to_dict('full')
        return self._track_dict

    @property
    def _meta(self):
        meta_filename = os.path.join(self.path_meta, '{}.json'.format(self.track['source_filename']))
        try:
            with self._open(meta_filename, 'r') as meta_filehandle:
                return json.load(meta_filehandle)
        except FileNotFoundError:
            log.warn('Unable to locate metadata for {id} - {meta_filename}'.format(id=self.track['id'], path_meta=self.path_meta, meta_filename=meta_filename))
            return {}

    def _get_source_filename(self, source_type):
        """
        Lookup metadata from source_filename
        From metadata lookup tags file (identifyable with .txt extension)
        Return relative path

        This is kind of reinventing the wheel as we do have code in `processmedia2`
        to parse this, but we want to reduce code dependencys and this is a single
        fairly understandbale, self contained, one off.
        """
        SOURCE_TYPE_EXTENSION_LOOKUP = {
            'tag': ('txt', ),
            'subtitles': ('ssa', 'srt'),
        }
        return os.path.join(
            self.path_source,
            first(
                filedata.get('relative')
                for filename, filedata in self._meta.get('scan', {}).items()
                if any(filename.endswith('.{}'.format(extension)) for extension in SOURCE_TYPE_EXTENSION_LOOKUP[source_type])
            ) or ''
        )

    def _get_source_file(self, source_type, errors='replace'):
        try:
            source_filename = self._get_source_filename(source_type)
            # If the charset is not utf8 (like some kind of latin variant) then
            # we will loose characters on save if 'replace' is used.
            # We cant use 'surrogateescape' we cant output this in pure utf-8 to the web interface
            # The web interface will only save the subtiles IF they have been editied on the web.
            # It may be worth erroring on web save if we detect the existing subtitles are not in utf-8
            with self._open(source_filename, 'tr', encoding='utf-8', errors=errors) as filehandle:
                return filehandle.read()
        except IOError as ex:
            log.error('Unable to load {} - {}'.format(source_filename, ex))
            return ''

    def _set_source_file(self, source_type, data):
        source_filename = self._get_source_filename(source_type)
        backup(source_filename, self.path_backup)
        with self._open(source_filename, 'w') as filehandle:
            filehandle.write(data)

    @property
    def tag_data_raw(self):
        return self._get_source_file('tag')
    @tag_data_raw.setter
    def tag_data_raw(self, tag_data):
        self._set_source_file('tag', tag_data)

    @property
    def tag_data(self):
        return {tuple(line.split(':')) for line in self.tag_data_raw.split('\n')}

    @property
    def subtitles(self):
        return self._get_source_file('subtitles')
    @subtitles.setter
    def subtitles(self, subtitles):
        self._set_source_file('subtitles', subtitles)

    @staticmethod
    def track_status(track_dict, status_tags=STATUS_TAGS, func_file_exists=lambda f: True):
        """
        Traffic light status system.
        returns a dict of status and reasons
        This just asserts based on
        """
        status_details = defaultdict(list)

        #func_is_folder(track_dict['source_filename'])
        if track_dict.get('duration', 0) <= 0:
            status_details['red'].append('invalid duration')

        # Tags
        # todo - how do we get requireg tags based on category? dont we have this info in 'search' somewhere?
        #        these should be enforced
        def check_tags(tag_list, status_key, message):
            for t in tag_list:
                if t not in track_dict['tags']:
                    status_details[status_key].append(message.format(t))
        check_tags(status_tags['recommended'], 'yellow', 'tag {0} suggested')
        check_tags(status_tags['required'], 'red', 'tag {0} missing')

        def flag_tags(tag_list, status_key):
            tags = track_dict.get('tags', {})
            for t in tag_list:
                message = ".\n".join(tags.get(t, [])) or (t in tags.get(None, []))
                if message:
                    status_details[status_key].append(message)
        flag_tags(status_tags['black'], 'black')
        flag_tags(status_tags['red'], 'red')
        flag_tags(status_tags['yellow'], 'yellow')
        flag_tags(status_tags['green'], 'green')

        # Lyrics
        # Do not do lyric checks if explicity stated they are not required.
        # Fugly code warning: (Unsure if both of these are needed for the hardsubs check)
        if ('hardsubs' not in track_dict['tags']) and ('hardsubs' not in track_dict['tags'].get(None, [])):
            lyrics = track_dict.get('lyrics', '')
            if not lyrics:
                status_details['red'].append('no lyrics')

        return {
            'status_details': status_details,
            'status': get_overall_status(status_details.keys()),
        }

    @property
    def status(self):
        return self.track_status(self.track, func_file_exists=lambda f: os.path.isfile(os.path.join(self.path_source, f)))


#-------------------------------------------------------------------------------
# Community Views
#-------------------------------------------------------------------------------

@view_config(
    context='karakara.traversal.ComunityContext',
    acquire_cache_bucket_func=acquire_cache_bucket_func,
)
def comunity(request):
    return action_ok()


@view_config(
    context='karakara.traversal.ComunityUploadContext',
)
def comunity_upload(request):
    return action_ok()


@view_config(
    context='karakara.traversal.ComunityListContext',
    acquire_cache_bucket_func=acquire_cache_bucket_func,
)
@comunity_only
def comunity_list(request):

    def _comnunity_list():

        def track_dict_to_status(track_dict):
            track_dict['status'] = ComunityTrack.factory(track_dict, request).status
            # Flatten tags into a single list
            track_dict['tags_flattened'] = [
                '{}:{}'.format(parent, tag)
                for parent, tags in track_dict['tags'].items()
                for tag in tags
            ]
            del track_dict['tags']
            del track_dict['attachments']
            del track_dict['lyrics']
            return track_dict

        # Get tracks from db
        tracks = [
            # , exclude_fields=('lyrics','attachments','image')
            track_dict_to_status(track.to_dict('full')) \
            for track in DBSession.query(Track) \
                .order_by(Track.source_filename) \
                .options( \
                    joinedload(Track.tags), \
                    joinedload(Track.attachments), \
                    joinedload('tags.parent'), \
                    undefer('lyrics'), \
                )
        ]

        # TODO: look at meta
        # TODO: look at path_upload

        return {
            'tracks': tracks,
            # TODO: add further details of currently processing files?
        }

    # Invalidate cache if db has updated
    #last_update_timestamp = last_update()
    #global list_cache_timestamp
    #if list_cache_timestamp is None or last_update_timestamp != list_cache_timestamp:
    #    list_cache_timestamp = last_update_timestamp
    #    #invalidate_list_cache(request)
    #    request.cache_bucket.invalidate(request=request)

    return action_ok(
        data=request.cache_bucket.get_or_create(_comnunity_list)
    )


@view_config(
    context='karakara.traversal.ComunityTrackContext',
    request_method='GET',
    #acquire_cache_bucket_func=acquire_cache_bucket_func,
)
@comunity_only
def comunity_track(request):
    log.debug('comunity_track {}'.format(request.context.id))
    ctrack = ComunityTrack.factory(request.context.id, request)
    return action_ok(data={
        'track': ctrack.track,
        'status': ctrack.status,
        'tag_data': ctrack.tag_data_raw,
        'subtitles': ctrack.subtitles,
    })
    # Todo - should throw action error with details on fail. i.e. if static files unavalable


@view_config(
    context='karakara.traversal.ComunityTrackContext',
    request_method='POST',
)
@comunity_only
def comunity_track_update(request):
    log.debug('comunity_track_update {}'.format(request.context.id))
    ctrack = ComunityTrack.factory(request.context.id, request)

    if 'tag_data' in request.params:
        ctrack.tag_data_raw = request.params['tag_data']
    if 'subtitles' in request.params:
        try:
            ctrack._get_source_file('subtitles', errors='strict')
        except UnicodeDecodeError as unicode_decode_error:
            raise action_error(
                'Source subtitle file is not in utf-8. '
                'Saving subtitles would loose information. '
                'Recommend that file is converted to utf-8 to enable web saving. '
                ' - {0} - {1}'.format(ctrack._get_source_filename('subtitles'), unicode_decode_error)
            )
        ctrack.subtitles = request.params['subtitles']

    return action_ok()


@view_config(
    context='karakara.traversal.ComunityProcessmediaLogContext',
)
@comunity_only
def comunity_processmedia_log(request):
    LOGFILE = request.registry.settings[PATH_PROCESSMEDIA2_LOG]
    REGEX_LOG_ITEM = re.compile(r'(?P<datetime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (?P<source>.+?) - (?P<loglevel>.+?) - (?P<message>.+?)(\n\d{2}-|$)', flags=re.DOTALL + re.IGNORECASE + re.MULTILINE)
    LEVELS = request.params.get('levels', 'WARNING,ERROR').split(',')
    try:
        # rrrrrrr - kind of a hack using ComunityTrack._open .. but it works ..
        with ComunityTrack._open(LOGFILE, 'rt') as filehandle:
            processmedia_log = [
                item
                for item in
                (
                    match.groupdict()
                    for match in REGEX_LOG_ITEM.finditer(filehandle.read())
                )
                if item.get('loglevel') in LEVELS
            ]
    except IOError:
        raise action_error(message='unable to open {}'.format(LOGFILE))
    return action_ok(data={
        'processmedia_log': processmedia_log,
    })
