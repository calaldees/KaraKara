import os

from libs.misc import postmortem, flatten

from processmedia_libs import add_default_argparse_args
from processmedia_libs.meta_manager import MetaManager
from processmedia_libs.processed_files_manager import ProcessedFilesManager

import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'


# Main -------------------------------------------------------------------------


def meta_tools(**kwargs):
    processed_files_manager = ProcessedFilesManager(kwargs['path_processed'])
    meta = MetaManager(kwargs['path_meta'])
    meta.load_all()



# Arguments --------------------------------------------------------------------

def get_args():
    """
    Command line argument handling
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description="""processmedia2 meta_tools
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

    postmortem(meta_tools, **args)
