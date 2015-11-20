
from libs.misc import postmortem, fast_scan, epoc, first
from processmedia_libs import add_default_argparse_args

from processmedia_libs.meta_manager import MetaManager
from processmedia_libs.processed_files_manager import ProcessedFilesManager
from processmedia_libs import subtitle_processor


from sqlalchemy.orm.exc import NoResultFound

from model.model_tracks import Track, Tag, Attachment, _attachment_types
from model import init_DBSession, DBSession, commit
from model.actions import get_tag, clear_all_tracks, last_update, delete_track


import logging
log = logging.getLogger(__name__)


def main(**kwargs):
    """
     - hash and identify primary key for track
     - import tags
     - import subtiles
     - cleanup db - any sources we don't have the actual processed files for - prune and remove from db
       - check this removes unnneeded attachments
    """
    meta = MetaManager(kwargs['path_meta'])
    importer = TrackImporter(meta_manager=meta, path_processed=kwargs['path_processed'])

    meta.load_all()  # mtime=epoc(last_update())

    processed_tracks = set(m.source_hash for m in meta.meta.values())

    for name in meta.meta.keys():
        importer.import_track(name)

    for unneeded_track_id in importer.imported_tracks - processed_tracks:
        log.warn('Removing unnneded tracks: %s', unneeded_track_id)
        delete_track(unneeded_track_id)
    commit()


class TrackImporter(object):

    def __init__(self, meta_manager=None, path_meta=None, path_processed=None, **kwargs):
        self.meta = meta_manager or MetaManager(path_meta)
        self.processed_files_manager = ProcessedFilesManager(path_processed)
        self.imported_tracks = set(t.id for t in DBSession.query(Track.id))

    def import_track(self, name):
        self.meta.load(name)
        m = self.meta.get(name)
        if not m.source_hash or m.source_hash in self.imported_tracks:
            return
        processed_files = self.processed_files_manager.get_all_processed_files_associated_with_source_hash(m.source_hash)
        if not self._has_required_files(processed_files):
            log.warn('%s does not have all required processde files', name)
            return

        log.info('Import: %s', name)
        track = Track()
        track.id = m.source_hash
        track.source_filename = name
        track.duration = m.source_details.get('duration')

        self._add_attachments(track, processed_files)
        self._add_lyrics(track, first(processed_files.get('srt')))
        self._add_tags(track, first(processed_files.get('tags')))

        DBSession.add(track)
        commit()

    def _has_required_files(self, processed_files):
        for k in ('video', 'preview', 'tags', 'image'):
            for processed_file in processed_files[k]:
                if not processed_file.exists:
                    log.warn('Missing processed file %s', processed_file.absolute)
                    return False
        return True

    def _add_attachments(self, track, processed_files):
        track.attachments.clear()
        for attachment_type in processed_files.keys() & set(_attachment_types.enums):
            for processed_file in processed_files[attachment_type]:
                attachment = Attachment()
                attachment.type = attachment_type
                attachment.location = processed_file.relative
                track.attachments.append(attachment)

    def _add_lyrics(self, track, processed_file_srt):
        if not processed_file_srt or not processed_file_srt.exists:
            log.warn('srt file missing unable to import lyrics')
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
                    log.warn('null tag %s', tag_string)

        for duplicate_tag in (tag for tag in track.tags if track.tags.count(tag) > 1):
            log.warn('Unneeded duplicate tag found %s', duplicate_tag)
            track.tags.remove(duplicate_tag)


# Arguments --------------------------------------------------------------------

def get_args():
    """
    Command line argument handling
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description="""processmedia2 importer
        """,
        epilog="""
        """
    )

    add_default_argparse_args(parser)

    parser.add_argument('--config_uri', action='store', help='', default='development.ini')

    args = vars(parser.parse_args())

    return args


if __name__ == "__main__":
    args = get_args()

    from pyramid.paster import get_appsettings
    logging.basicConfig(level=args['log_level'])
    settings = get_appsettings(args['config_uri'])
    init_DBSession(settings)

    postmortem(main, **args)
