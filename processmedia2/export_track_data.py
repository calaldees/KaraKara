from functools import partial
import json

from clint.textui.progress import bar as progress_bar

from calaldees.files.scan import fast_scan

from processmedia_libs.meta_overlay import MetaManagerExtended
from processmedia_libs import PENDING_ACTION

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
    processed_files_lookup = frozenset(f.relative for f in fast_scan(meta_manager.processed_files_manager.path))

    def _tracks():
        for name in progress_bar(meta_manager.meta.keys()):
            log.debug(f'Attempting: {name}')
            meta_manager.load(name)
            m = meta_manager.get(name)

            # Abort id not processed
            if not m.source_hash:
                log.debug(f'Unprocessed (no source_hash): {name}')
                stats['meta_unprocessed'].add(name)
                continue

            # Abort if any missing files
            missing_processed_files = frozenset(f.relative for f in m.processed_files.values()) - processed_files_lookup
            if missing_processed_files:
                log.debug(f'{missing_processed_files=}')
                # If we are missing any files but we have a source hash,
                # we may have some of the derived media missing.
                # Explicitly mark the item for re-encoding
                if PENDING_ACTION['encode'] not in m.pending_actions:  # Feels clunky to manage this as a list? maybe a set?
                    m.pending_actions.append(PENDING_ACTION['encode'])
                    #meta_manager.save(name)  # Feels clunky
                log.warning('Missing (processed files) abort import: %s', name)
                stats['missing_processed_aborted'].add(name)
                continue

            log.debug(f'Export: {name}')

            def _get_srt():
                processed_file_srt = m.processed_files.get('srt')
                if not processed_file_srt or not processed_file_srt.exists:
                    log.debug(f'{processed_file_srt=} missing - unable to import srt')
                    return
                with open(processed_file_srt.absolute, 'rt', encoding='utf-8', errors='ignore') as srt_file:
                    return srt_file.read()

            def _get_tags():
                processed_file_tags = m.processed_files.get('tags')
                with open(processed_file_tags.absolute, 'rt', encoding='utf-8', errors='ignore') as tag_file:
                    return tag_file.read().strip().strip("\ufeff")

            yield m.source_hash, {
                'source_filename': name,
                'duration': m.source_details.get('duration'),
                'attachments': tuple(
                    {
                        'use': processed_file.attachment_type,
                        'url': processed_file.relative,
                        'mime': processed_file.mime,
                    }
                    for processed_file in m.processed_files.values()
                ),
                'srt': _get_srt(),
                'tags': _get_tags(),
            }
            stats['meta_exported'].add(name)

    with open(kwargs['path_static_track_list'], 'wt') as filehandle:
        json.dump(dict(_tracks()), filehandle)

    return stats


def additional_arguments(parser):
    parser.add_argument('--path_static_track_list', action='store', help='the path to output json data', required=True)


if __name__ == "__main__":
    from _main import main
    main(
        'export_track_data', export_track_data, folder_type_to_derive_mtime='meta',
        additional_arguments_function=additional_arguments,
    )
