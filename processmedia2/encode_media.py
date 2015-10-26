import os.path
import tempfile

from libs.misc import postmortem, hashfile, freeze, first
from libs.file import FolderStructure

from processmedia_libs import add_default_argparse_args
from processmedia_libs.meta_manager import MetaManager, FileItemWrapper
from processmedia_libs.processed_files_manager import ProcessedFilesManager
from processmedia_libs import external_tools

import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'


def main(**kwargs):
    meta = MetaManager(kwargs['path_meta'])
    meta.load_all()

    encoder = Encoder(meta, **kwargs)

    # In the full system, encode will probably be driven from a rabitmq endpoint.
    # For testing locally we are monitoring the 'pendings_actions' list
    for name in ('Cuticle Tantei Inaba - OP - Haruka Nichijou no Naka de', ):
    #for name in (m.name for m in meta.meta.values() if m.pending_actions):
        encoder.encode(name)


class Encoder(object):
    """
        consume for
         - update tags
         - extract lyrics
         - encode media
        ENCODE (queue consumer)
            listen to queue
            -Encode-
            Update meta destination hashs
            -CLEANUP-
            prune unneeded files from destination
            trigger importer
    choose encode type
     - video
     - video + sub
     - video + audio
     - image + sub + audio
    input hashs cmp output hash
    encode hi-res
     - normalize audio
     - normalize subtitles
       - srt to ssa
       - rewrite playres
       - remove dupes
       - add next line
    preview encode
    gen thumbnail images
    extract subs
    """

    def __init__(self, meta_manager=None, path_meta=None, path_processed=None, path_source=None, **kwargs):
        self.meta = meta_manager or MetaManager(path_meta)
        self.destination = FolderStructure.factory(path_processed)
        self.fileitem_wrapper = FileItemWrapper(path_source)
        self.processed_files_manager = ProcessedFilesManager(path_processed)

    def _get_meta(self, name):
        self.meta.load(name)
        return self.meta.get(name)

    def encode(self, name):
        """
        Todo: save the meta on return ... maybe use a context manager
        """
        log.info('Encode: %s', name)
        self.meta.load(name)
        m = self.meta.get(name)
        self._encode_primary_video_from_meta(m)
        self._encode_preview_video_from_meta(m)
        self._encode_images_from_meta(m)
        self.meta.save(name)

    def _encode_primary_video_from_meta(self, m):
        # 1.) Calculate starting files and target files
        source_files = self.fileitem_wrapper.wrap_scan_data(m)
        target_file = self.processed_files_manager.get_video_file(f['hash'] for f in source_files.values() if f)

        # 2.) Assertain if encoding is actually needed by hashing sources and comparing input and output hashs
        if target_file.exists:
            m.processed_data.setdefault('main', {})['hash'] = target_file.hash
            log.info('Processed Destination was created with the same input sources - no encoding required')
            return True

        with tempfile.TemporaryDirectory() as tempdir:
            # 3.) Convert souce formats into appropriate formats for video encoding

            # 3.a) Convert Image to Video
            if source_files['image'] and not source_files['video']:
                log.warn('image to video conversion is not currently implemented')
                return False

            # 3.b) Convert srt to ssa
            if not source_files['sub'].get('ext') == 'ssa':
                log.warn('convert subs to ssa no implemented yet')
                source_files['sub'] = {'absolute': None}
                return False

            # 4.) Encode
            encode_steps = (
                # 4.a) Render video with subtitles (without audio)
                lambda: external_tools.encode_video(
                    source=source_files['video']['absolute'],
                    sub=source_files['sub'].get('absolute'),
                    destination=os.path.join(tempdir, 'video.avi'),
                ),

                # 4.b) Render audio and normalize
                lambda: external_tools.encode_audio(
                    source=source_files['audio'].get('absolute') or source_files['video'].get('absolute'),
                    destination=os.path.join(tempdir, 'audio.wav'),
                ),

                # 4.c) Mux Video and Audio
                lambda: external_tools.mux(
                    video=os.path.join(tempdir, 'video.avi'),
                    audio=os.path.join(tempdir, 'audio.wav'),
                    destination=os.path.join(tempdir, 'mux.mp4'),
                )
            )
            for encode_step in encode_steps:
                encode_success, cmd_result = encode_step()
                if not encode_success:
                    import pdb ; pdb.set_trace()
                    return False

            # 5.) Move the newly encoded file to the target path
            target_file.move(os.path.join(tempdir, 'mux.mp4'))
            m.processed_data.setdefault('main', {})['hash'] = target_file.hash

        return True

    def _encode_preview_video_from_meta(self, m):
        source_hash = m.processed_data.setdefault('main', {}).get('hash')
        source_file = self.processed_files_manager.get_video_file(source_hash)
        target_file = self.processed_files_manager.get_preview_file(source_hash)

        if not source_file.exists:
            log.warn('No source video to encode preview from')
            return False

        if target_file.exists:
            #m.processed_data.setdefault('preview', {})['hash'] = target_file.hash
            log.info('Processed Destination was created with the same input sources - no encoding required')
            return True

        with tempfile.TemporaryDirectory() as tempdir:
            preview_file = os.path.join(tempdir, 'preview.mp4')
            encode_success, cmd_result = external_tools.encode_preview_video(
                source=source_file.absolute,
                destination=preview_file,
            )
            if not encode_success:
                import pdb ; pdb.set_trace()
                return False
            target_file.move(preview_file)
            #m.processed_data.setdefault('preview', {})['hash'] = target_file.hash

        return True

    def _encode_images_from_meta(self, m, num_images=4):
        source_hash = m.processed_data.setdefault('main', {}).get('hash')
        source_file = self.processed_files_manager.get_video_file(source_hash)
        image_hashs = m.processed_data.setdefault('image', {}).setdefault('hash', [])
        image_hashs[:] = []

        target_files = tuple(
            self.processed_files_manager.get_image_file(source_hash, index)
            for index in range(num_images)
        )
        if all(target_file.exists for target_file in target_files):
            log.info('Processed Destination was created with the same input sources - no thumbnail gen required')
            return True

        video_duration = external_tools.probe_media(source_file.absolute).get('duration')
        if not video_duration:
            log.warn('Unable to assertain video duration; unable to extact images')
            return False
        times = (float("%.3f" % (video_duration * offset)) for offset in (x/(num_images+1) for x in range(1, num_images+1)))

        for index, time in enumerate(times):
            target_file = target_files[index]
            encode_succes, cmd_result = external_tools.extract_image(source_file.absolute, target_file.absolute, time)
            if not encode_succes:
                import pdb ; pdb.set_trace()
                return False
            image_hashs.append(target_file.hash)

        return True


# Arguments --------------------------------------------------------------------

def get_args():
    """
    Command line argument handling
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description="""processmedia2 encoder
        """,
        epilog="""
        """
    )

    add_default_argparse_args(parser)

    args = vars(parser.parse_args())

    return args


if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=args['log_level'])

    postmortem(main, **args)
