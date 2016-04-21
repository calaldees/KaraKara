import os

from libs.misc import postmortem, flatten

from processmedia_libs import add_default_argparse_args
from processmedia_libs.meta_manager import MetaManager
from processmedia_libs.processed_files_manager import ProcessedFilesManager

import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'


# Main -------------------------------------------------------------------------


def cleanup_media(**kwargs):
    processed_files_manager = ProcessedFilesManager(kwargs['path_processed'])
    meta = MetaManager(kwargs['path_meta'])
    meta.load_all()

    known_file_hashs = {
        processed_file.hash
        for processed_file in flatten(
            processed_files_manager.get_all_processed_files_associated_with_source_hash(source_hash).values()
            for source_hash in meta.source_hashs
        )
    }
    unlinked_files = (f for f in processed_files_manager.scan if f.file_no_ext and f.file_no_ext not in known_file_hashs)

    for unlinked_file in unlinked_files:
        os.remove(unlinked_file)


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

    args_dict = vars(parser.parse_args())

    return args_dict


if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=args['log_level'])

    postmortem(cleanup_media, **args)
