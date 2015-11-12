
from libs.misc import postmortem
from processmedia_libs import add_default_argparse_args

from processmedia_libs.meta_manager import MetaManager

from model.model_tracks import Track, Tag, Attachment, Lyrics, _attachment_types
from model.actions import last_update

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
    meta.load_all()


class Importer(object):
    pass


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

    args = vars(parser.parse_args())

    return args


if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=args['log_level'])

    postmortem(main, **args)
