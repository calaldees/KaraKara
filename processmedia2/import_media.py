import sys
from pprint import pprint
from functools import partial
import urllib.request
import json

from clint.textui.progress import bar as progress_bar

from calaldees.data import first
from calaldees.debug import postmortem
from calaldees.files.scan import fast_scan
from calaldees.date_tools import epoc

from processmedia_libs import PENDING_ACTION
from processmedia_libs.meta_overlay import MetaManagerExtended
from processmedia_libs import subtitle_processor_with_codecs as subtitle_processor
from processmedia_libs.fileset_change_monitor import FilesetChangeMonitor

import logging
log = logging.getLogger(__name__)


class TrackNotProcesedException(Exception):
    pass


class TrackMissingProcessedFiles(Exception):
    def __init__(self, id, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.id = id


def _track_api(host, data={}, method='GET'):
    try:
        return json.load(
            urllib.request.urlopen(
                urllib.request.Request(
                    f'http://{host}/track_import?format=json',
                    data=json.dumps(data).encode('utf8'),
                    headers={'content-type': 'application/json'},
                    method=method,
                ),
                #timeout=120,
            )
        )
    except urllib.error.URLError as ex:
        log.error(f'track_import failure - {host} - {ex} - {data}')
        sys.exit(1)


def _generate_track_dict(name, meta_manager=None, processed_files_lookup=None, existing_track_ids=None):
    """
    """
    log.debug('Attempting: %s', name)

    meta_manager.load(name)
    m = meta_manager.get(name)

    if not m.source_hash:
        raise TrackNotProcesedException()

    # Abort if any missing files
    missing_processed_files = {
        (file_type, processed_file)
        for file_type, processed_file in m.processed_files.items()
        if processed_file.relative not in processed_files_lookup
    }
    for file_type, processed_file in missing_processed_files:
        log.debug('Missing processed file: {0} - {1}'.format(file_type, processed_file.absolute))
    if missing_processed_files:
        # If we are missing any files but we have a source hash,
        # we may have some of the derived media missing.
        # Explicitly mark the item for reencoding
        if PENDING_ACTION['encode'] not in m.pending_actions:  # Feels clunky to manage this as a list? maybe a set?
            m.pending_actions.append(PENDING_ACTION['encode'])
            meta_manager.save(name)  # Feels clunky
        raise TrackMissingProcessedFiles(id=m.source_hash in existing_track_ids and m.source_hash)

    if m.source_hash in existing_track_ids:
        log.debug('Exists: {name}'.format(name=name))  # TODO: replace with formatstring
        return

    log.debug('Import: {name}'.format(name=name))  # TODO: replace with formatstring

    def _get_attachments():
        return [
            {
                'type': processed_file.attachment_type,
                'location': processed_file.relative,
            }
            for processed_file in m.processed_files.values()
        ]

    def _get_lyrics():
        processed_file_srt = m.processed_files.get('srt')
        if not processed_file_srt or not processed_file_srt.exists:
            log.warning('srt file missing unable to import lyrics')
            return
        return "\n".join(subtitle.text for subtitle in subtitle_processor.parse_subtitles(filename=processed_file_srt.absolute))

    def _get_tags():
        processed_file_tags = m.processed_files.get('tags')
        with open(processed_file_tags.absolute, 'rt', encoding='utf-8', errors='ignore') as tag_file:
            return tuple(tag_string.strip() for tag_string in tag_file)

    return {
        'id': m.source_hash,
        'source_filename': name,
        'duration': m.source_details.get('duration'),
        'lyrics': _get_lyrics(),
        'attachments': _get_attachments(),
        'tags': _get_tags(),
    }
    #self.existing_track_ids.add(m.source_hash)  # HACK!! .. we should not have duplicate hashs's in the source set. This is a temp patch


def import_media(**kwargs):
    """
    """
    stats = dict(meta_set=set(), meta_imported=set(), meta_unprocessed=set(), db_removed=list(), missing_processed_deleted=set(), missing_processed_aborted=set(), db_start=set(), meta_hash_matched_db_hash=set())

    track_api = partial(_track_api, kwargs['api_host'])

    meta_manager = MetaManagerExtended(**kwargs)
    meta_manager.load_all()  # mtime=epoc(last_update())
    processed_track_ids = set(meta_manager.source_hashs)
    processed_files_lookup = set(f.relative for f in fast_scan(meta_manager.processed_files_manager.path))
    existing_tracks = track_api()['data']['tracks']
    existing_track_ids = existing_tracks.keys()

    generate_track_dict = partial(_generate_track_dict, meta_manager=meta_manager, existing_track_ids=existing_track_ids, processed_files_lookup=processed_files_lookup)

    stats['db_start'] = set(existing_tracks.values())
    stats['meta_set'] = set(m.name for m in meta_manager.meta_items if m.source_hash)

    tracks_to_add = []
    track_ids_to_delete = []

    log.info('Importing tracks - Existing:{} Processed:{}'.format(len(existing_track_ids), len(processed_track_ids)))  # TODO: replace with formatstring
    for name in progress_bar(meta_manager.meta.keys()):
        try:
            track = generate_track_dict(name)
            if track:
                stats['meta_imported'].add(name)
                #tracks_to_add.append(track)
                track_api([track], method='POST')
            else:
                stats['meta_hash_matched_db_hash'].add(name)
        except TrackNotProcesedException:
            log.debug('Unprocessed (no source_hash): %s', name)
            stats['meta_unprocessed'].add(name)
        except TrackMissingProcessedFiles as ex:
            if ex.id:
                log.warning('Missing (processed files) delete existing: %s', name)
                track_ids_to_delete.append(ex.id)
                stats['missing_processed_deleted'].add(name)
            else:
                log.warning('Missing (processed files) abort import: %s', name)
                stats['missing_processed_aborted'].add(name)

    for unneeded_track_id in existing_track_ids - processed_track_ids:
        log.warning('Remove: %s', unneeded_track_id)
        stats['db_removed'].append(existing_tracks[unneeded_track_id])
        track_ids_to_delete.append(unneeded_track_id)

    log.info("""{api_host} -> Add:{add_count} Delete:{delete_count}""".format(
        api_host=kwargs['api_host'],
        add_count=len(tracks_to_add),
        delete_count=len(track_ids_to_delete),
    ))  # TODO: replace with formatstring
    #track_api(tracks_to_add, method='POST')
    track_api(track_ids_to_delete, method='DELETE')

    stats['db_end'] = track_api()['data']['tracks'].values()

    #assert stats['db_end'] == stats['meta_hash_matched_db_hash'] | stats['meta_imported']  # TODO! Reinstate this
    return stats


# Main -------------------------------------------------------------------------

def additional_arguments(parser):
    parser.add_argument('--api_host', action='store', help='', default='')
    parser.add_argument('--stat_limit', type=int, help='Max number of metanames to display in summary before replacing them with a count', default=100)


if __name__ == "__main__":
    from _main import main
    stats = main(
        'import_media', import_media, folder_type_to_derive_mtime='meta',
        additional_arguments_function=additional_arguments,
    )
    pprint({k: len(v) if len(v) > import_media.calling_kwargs['stat_limit'] else v for k, v in stats.items()})
