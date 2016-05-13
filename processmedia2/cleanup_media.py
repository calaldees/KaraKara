import os

from libs.misc import postmortem

from processmedia_libs import add_default_argparse_args, parse_args
from processmedia_libs.meta_overlay import MetaManagerExtended

import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'


# Main -------------------------------------------------------------------------


def cleanup_media(**kwargs):
    meta_manager = MetaManagerExtended(**kwargs)
    meta_manager.load_all()

    all_known_file_hashs = {
        processed_file.hash
        for m in meta_manager.meta_items
        for processed_file in m.processed_files.values()
    }
    unlinked_files = (f for f in meta_manager.processed_files_manager.scan if f.file_no_ext and f.file_no_ext not in all_known_file_hashs)

    for unlinked_file in unlinked_files:
        os.remove(unlinked_file.absolute)


# Arguments --------------------------------------------------------------------

def get_args():
    """
    Command line argument handling
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description="""processmedia2 cleanup
        """,
        epilog="""
        """
    )

    add_default_argparse_args(parser)

    return parse_args(parser)


if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=args['log_level'])

    postmortem(cleanup_media, **args)
