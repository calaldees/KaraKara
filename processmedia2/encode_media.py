from processmedia_libs import add_default_argparse_args

from libs.misc import postmortem
from libs.file import FolderStructure

from processmedia_libs.meta_manager import MetaManager

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

    def __init__(self, meta_manager=None, path_meta=None, path_processed=None, **kwargs):
        self.meta = meta_manager or MetaManager(path_meta)
        self.destination = FolderStructure.factory(path_processed)

    def _get_meta(self, name):
        self.meta.load(name)
        return self.meta.get(name)

    def encode(self, name):
        m = self._get_meta(name)
        print(m.name)
        import pdb ; pdb.set_trace()
        m.get_files_for('video')


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
