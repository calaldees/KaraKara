from functools import partial, reduce
import json
import re
import gzip

from clint.textui.progress import bar as progress_bar

from calaldees.files.scan import fast_scan

from processmedia_libs.meta_overlay import MetaManagerExtended
from processmedia_libs import PENDING_ACTION
from processmedia_libs.subtitle_processor_with_codecs import parse_subtitles
from processmedia_libs.tag_processor import parse_tags

import logging
log = logging.getLogger(__name__)


def export_track_data(**kwargs):
    """
    """
    stats = {
        name: set()
        for name in {'meta_exported', 'meta_unprocessed', 'missing_processed_deleted', 'missing_processed_aborted'}
    }

    meta_manager = MetaManagerExtended(**kwargs)
    meta_manager.load_all()  # mtime=epoc(last_update())
    processed_files_lookup = frozenset(f.relative for f in fast_scan(str(meta_manager.processed_files_manager.path)))

    def _tracks():
        for name in progress_bar(meta_manager.meta.keys()):
            log.debug(f'Attempting: {name}')
            meta_manager.load(name)
            m = meta_manager.get(name)

            # Abort if duration not known
            if not m.source_details.get('duration'):
                log.warning('Missing (duration) abort import: {name}')
                stats['missing_processed_aborted'].add(name)  # TODO: rename
                continue

            # Abort if any missing files
            missing_processed_files = frozenset(str(f.relative) for f in m.processed_files.values()) - processed_files_lookup
            if missing_processed_files:
                log.debug(f'{missing_processed_files=}')
                # If we are missing any files but we have a source hash,
                # we may have some of the derived media missing.
                # Explicitly mark the item for re-encoding
                if PENDING_ACTION['encode'] not in m.pending_actions:  # Feels clunky to manage this as a list? maybe a set?
                    m.pending_actions.append(PENDING_ACTION['encode'])
                    #meta_manager.save(name)  # Feels clunky
                log.warning('Missing (processed files) abort import: {name}')
                stats['missing_processed_aborted'].add(name)
                continue

            log.debug(f'Export: {name}')

            def _get_attachments():
                def _reduce(accumulator, processed_file):
                    accumulator.setdefault(processed_file.type.attachment_type, []).append({
                        'mime': processed_file.type.mime,
                        'path': str(processed_file.relative),
                    })
                    return accumulator
                return reduce(_reduce, m.processed_files.values(), {})

            def _get_lyrics():
                source_file_sub = m.source_files.get('sub')
                if not source_file_sub or not source_file_sub.file.is_file():
                    log.debug(f'{source_file_sub=} missing - unable to import srt')
                    return
                with source_file_sub.file.open('rt') as filehandle:
                    subtitles = parse_subtitles(filehandle=filehandle)
                return '\n'.join(subtitle.text for subtitle in subtitles)

            def _get_tags():
                source_file_tag = m.source_files.get('tag')
                with source_file_tag.file.open('rt', encoding='utf-8', errors='ignore') as tag_file:
                    return parse_tags(tag_file.read())

            track_id = re.sub('[^0-9a-zA-Z]+', '_', name)
            yield track_id, {
                'id': track_id,
                'source_hash': m.source_hash,
                'source_filename': name,
                'duration': m.source_details['duration'],
                'attachments': _get_attachments(),
                'lyrics': _get_lyrics(),
                'tags': _get_tags(),
            }
            stats['meta_exported'].add(name)

    assert kwargs['path_static_track_list']
    data = json.dumps(dict(_tracks()), default=tuple)
    with open(kwargs['path_static_track_list'], 'wt') as filehandle:
        filehandle.write(data)
    if kwargs['gzip']:
        with gzip.open(kwargs['path_static_track_list']+".gz", 'wb') as filehandle:
            filehandle.write(data.encode('utf8'))

    return stats


def additional_arguments(parser):
    parser.add_argument('--path_static_track_list', action='store', help='the path to output json data')
    parser.add_argument('--gzip', action='store_true', default=False, help='also write out track_list.json.gz')


if __name__ == "__main__":
    from _main import main
    main(
        'export_track_data', export_track_data, folder_type_to_derive_mtime='meta',
        additional_arguments_function=additional_arguments,
    )
