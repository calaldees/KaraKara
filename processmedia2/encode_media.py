import os.path
import tempfile

from libs.misc import postmortem, hashfile, freeze, first
from libs.file import FolderStructure

from processmedia_libs import add_default_argparse_args
from processmedia_libs.meta_manager import MetaManager, FileItemWrapper
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
    for name in (m.name for m in meta.meta.values() if m.pending_actions):
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

    def _get_meta(self, name):
        self.meta.load(name)
        return self.meta.get(name)

    def encode(self, name):
        """
        Todo: save the meta on return ... maybe use a context manager
        """
        m = self._get_meta(name)

        files = self.fileitem_wrapper.wrap_scan_data(m)

        # 1.) Assertain if encoding is actually needed by comparing input and output hashs
        source_hash = str(frozenset(f['hash'] for f in files.values() if f).__hash__()).replace('-', 'x')
        if m.processed_data.setdefault('main', {}).get('source_hash') == source_hash:
            log.info('Processed Destination was created with the same input sources - no encoding required')
            return True
        else:
            m.processed_data['main']['source_hash'] = source_hash  # This will not be saved to the meta until the end

        if first(self.destination.scan(lambda file_item: file_item.file_no_ext == source_hash)):
            log.info('Processed Destination already exisits - no encoding required - meta now links to destination')
            # TODO: SAVE THE META
            return True

        with tempfile.TemporaryDirectory() as tempdir:
            # 2.) Convert souce formats into appropriate formats for video encoding

            # 2.a) Convert Image to Video
            if files['image'] and not files['video']:
                log.warn('image to video conversion is not currently implemented')
                return False

            # 2.b) Convert srt to ssa
            if not files['sub'].get('ext') == 'ssa':
                log.warn('convert subs to ssa no implemented yet')
                files['sub'] = {'absolute': None}
                return False

            # 3.) Encode
            encode_steps = (
                # 3.a) Render video with subtitles (without audio)
                lambda: external_tools.encode_video(
                    source=files['video']['absolute'],
                    sub=files['sub'].get('absolute'),
                    destination=os.path.join(tempdir, 'video.avi'),
                ),

                # 3.b) Render audio and normalize
                lambda: external_tools.encode_audio(
                    source=files['audio'].get('absolute') or files['video'].get('absolute'),
                    destination=os.path.join(tempdir, 'audio.wav'),
                ),

                # 3.c) Mux Video and Audio
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

            import pdb ; pdb.set_trace()
            print('Done')

            # 4.) Moved procesed file
            # move_to_processed(filepath, 'main')

        #self.meta.save(name)

    def encode_preview(self, name):
        log.warn('preview encoding unimplemented')
        # Generate low bitrate preview
        # move_to_processed(filepath, 'preview')



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
