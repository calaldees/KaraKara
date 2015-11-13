
from libs.misc import postmortem, fast_scan, epoc
from processmedia_libs import add_default_argparse_args

from processmedia_libs.meta_manager import MetaManager
from processmedia_libs.processed_files_manager import ProcessedFilesManager
from processmedia_libs import subtitle_processor


from sqlalchemy.orm.exc import NoResultFound

from model.model_tracks import Track, Tag, Attachment, _attachment_types
from model import init_DBSession, DBSession, commit
from model.actions import get_tag, clear_all_tracks, last_update


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

    for unneeded_track in importer.imported_tracks - processed_tracks:
        log.warn('delete %s', unneeded_track)


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

        log.info('Import: %s', name)
        track = Track()
        track.id = m.source_hash
        track.source_filename = name

        track.duration = 0  # TODO

        self._add_attachments(track)
        self._add_lyrics(track)

        DBSession.add(track)
        commit()

    def _add_attachments(self, track):
        processed_files = self.processed_files_manager.get_all_processed_files_associated_with_source_hash(track.id)
        track.attachments.clear()
        for attachment_type in processed_files.keys() & _attachment_types.enums:
            for processed_file in processed_files[attachment_type]:
                attachment = Attachment()
                attachment.type = attachment_type
                attachment.location = processed_file.relative

                track.attachments.append(attachment)

    def _add_lyrics(self, track):
        subtitles = subtitle_processor.parse_subtiles(
            filename=self.processed_files_manager.get_processed_file(track.id, 'srt').absolute
        )
        track.lyrics = "\n".join(subtitle.text for subtitle in subtitles)
        import pdb ; pdb.set_trace()


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
