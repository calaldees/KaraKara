from collections import defaultdict
from pprint import pprint

from clint.textui.progress import bar as progress_bar

from libs.misc import postmortem, fast_scan, epoc, first
from processmedia_libs import PENDING_ACTION

from processmedia_libs.meta_overlay import MetaManagerExtended
from processmedia_libs import subtitle_processor_with_codecs as subtitle_processor
from processmedia_libs.fileset_change_monitor import FilesetChangeMonitor

from sqlalchemy.orm.exc import NoResultFound

from karakara.model.model_tracks import Track, Tag, Attachment, _attachment_types
from karakara.model import init_DBSession, DBSession, commit
from karakara.model.actions import get_tag, clear_all_tracks, last_update, delete_track

ATTACHMENT_TYPES = set(_attachment_types.enums)

import logging
log = logging.getLogger(__name__)


class TrackNotProcesedException(Exception):
    pass


class TrackMissingProcessedFiles(Exception):
    def __init__(self, id, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.id = id


def import_media(**kwargs):
    """
    """
    stats = dict(meta_set=set(), meta_imported=set(), meta_unprocessed=set(), db_removed=list(), missing_processed_deleted=set(), missing_processed_aborted=set(), db_start=set(), meta_hash_matched_db_hash=set())

    def get_db_track_names():
        return set(t.source_filename for t in DBSession.query(Track.source_filename))

    meta_manager = MetaManagerExtended(**kwargs)
    importer = TrackImporter(meta_manager=meta_manager)
    stats['db_start'] = get_db_track_names()

    meta_manager.load_all()  # mtime=epoc(last_update())

    meta_processed_track_ids = set(meta_manager.source_hashs)
    stats['meta_set'] = set(m.name for m in meta_manager.meta_items if m.source_hash)

    for name in progress_bar(meta_manager.meta.keys()):
        try:
            if importer.import_track(name):
                stats['meta_imported'].add(name)
            else:
                stats['meta_hash_matched_db_hash'].add(name)
        except TrackNotProcesedException:
            log.debug('Unprocessed (no source_hash): %s', name)
            stats['meta_unprocessed'].add(name)
        except TrackMissingProcessedFiles as ex:
            if ex.id:
                log.warning('Missing (processed files) delete existing: %s', name)
                delete_track(ex.id)
                commit()
                stats['missing_processed_deleted'].add(name)
            else:
                log.warning('Missing (processed files) abort import: %s', name)
                stats['missing_processed_aborted'].add(name)

    for unneeded_track_id in importer.exisiting_track_ids - meta_processed_track_ids:
        log.warning('Remove: %s', unneeded_track_id)
        stats['db_removed'].append(DBSession.query(Track).get(unneeded_track_id).source_filename or unneeded_track_id)
        delete_track(unneeded_track_id)
        commit()

    stats['db_end'] = get_db_track_names()

    #assert stats['db_end'] == stats['meta_hash_matched_db_hash'] | stats['meta_imported']  # TODO! Reinstate this

    return stats


class TrackImporter(object):

    def __init__(self, meta_manager=None):  # , path_meta=None, path_processed=None, **kwargs
        self.meta_manager = meta_manager #or MetaManager(path_meta)
        self.exisiting_track_ids = set(t.id for t in DBSession.query(Track.id))
        self.existing_files_lookup = set(f.relative for f in fast_scan(self.meta_manager.processed_files_manager.path))

    def import_track(self, name):
        log.debug('Attemping: %s', name)

        self.meta_manager.load(name)
        m = self.meta_manager.get(name)

        if not m.source_hash:
            raise TrackNotProcesedException()

        if self._missing_files(m.processed_files):
            # If we are missing any files but we have a source hash,
            # we may have some of the derived media missing.
            # Explicity mark the item for reencoding
            if PENDING_ACTION['encode'] not in m.pending_actions:  # Feels clunky to manage this as a list? maybe a set?
                m.pending_actions.append(PENDING_ACTION['encode'])
                self.meta_manager.save(name)  # Feels clunky
            raise TrackMissingProcessedFiles(id=m.source_hash in self.exisiting_track_ids and m.source_hash)

        if m.source_hash in self.exisiting_track_ids:
            log.debug('Exists: %s', name)
            return False

        log.info('Import: %s', name)
        track = Track()
        track.id = m.source_hash
        track.source_filename = name
        track.duration = m.source_details.get('duration')

        self._add_attachments(track, m.processed_files)
        self._add_lyrics(track, m.processed_files.get('srt'))
        self._add_tags(track, m.processed_files.get('tags'))

        DBSession.add(track)
        commit()
        self.exisiting_track_ids.add(m.source_hash)  # HACK!! .. we should not have duplicate hashs's in the source set. This is a temp patch

        return True

    def _missing_files(self, processed_files):
        missing_processed_files = {
            (file_type, processed_file)
            for file_type, processed_file in processed_files.items()
            if processed_file.relative not in self.existing_files_lookup  # not processed_file.exists
        }
        for file_type, processed_file in missing_processed_files:
            log.debug('Missing processed file: {0} - {1}'.format(file_type, processed_file.absolute))
        return missing_processed_files

    def _add_attachments(self, track, processed_files):
        track.attachments.clear()
        for processde_file in processed_files.values():
            assert processde_file.attachment_type in ATTACHMENT_TYPES
            attachment = Attachment()
            attachment.type = processde_file.attachment_type
            attachment.location = processde_file.relative
            track.attachments.append(attachment)

    def _add_lyrics(self, track, processed_file_srt):
        if not processed_file_srt or not processed_file_srt.exists:
            log.warning('srt file missing unable to import lyrics')
            return
        subtitles = subtitle_processor.parse_subtitles(filename=processed_file_srt.absolute)
        track.lyrics = "\n".join(subtitle.text for subtitle in subtitles)

    def _add_tags(self, track, processed_file_tags):
        track.tags.clear()

        with open(processed_file_tags.absolute, 'r') as tag_file:
            for tag_string in tag_file:
                tag_string = tag_string.strip()
                tag = get_tag(tag_string, create_if_missing=True)
                if tag:
                    track.tags.append(tag)
                elif tag_string:
                    log.warning('null tag %s', tag_string)

        for duplicate_tag in (tag for tag in track.tags if track.tags.count(tag) > 1):
            log.warning('Unneeded duplicate tag found %s in %s', duplicate_tag, track.source_filename)
            track.tags.remove(duplicate_tag)


# Main -------------------------------------------------------------------------

def additional_arguments(parser):
    parser.add_argument('--config_uri', action='store', help='', default='development.ini')
    parser.add_argument('--stat_limit', type=int, help='Max number of metanames to display in summary before replacing them with a count', default=100)


def _import_media(*args, **kwargs):
    from pyramid.paster import get_appsettings
    settings = get_appsettings(kwargs['config_uri'])
    init_DBSession(settings)
    return import_media(*args, **kwargs)

if __name__ == "__main__":
    from _main import main
    stats = main(
        'import_media', _import_media, mtime_path='meta',
        additional_arguments_function=additional_arguments,
    )
    pprint({k: len(v) if len(v) > _import_media.calling_kwargs['stat_limit'] else v for k, v in stats.items()})
