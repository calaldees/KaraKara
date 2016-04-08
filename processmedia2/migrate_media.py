import os

from libs.misc import postmortem, file_extension_regex, fast_scan_regex_filter, flatten
from libs.file import FolderStructure

from processmedia_libs import add_default_argparse_args, ALL_EXTS

from scan_media import DEFAULT_IGNORE_FILE_REGEX

import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'


# Main -------------------------------------------------------------------------


def migrate_media(**kwargs):
    # Read file structure into memory
    folder_structure = FolderStructure.factory(
        path=kwargs['path_source'],
        search_filter=fast_scan_regex_filter(
            file_regex=file_extension_regex(ALL_EXTS),
            ignore_regex=DEFAULT_IGNORE_FILE_REGEX,
        )
    )

    #import pdb ; pdb.set_trace()
    #def ttt(fff):
    #    import pdb ; pdb.set_trace()
    #    return True
    #ttt = tuple(folder_structure.scan(ttt))


# Arguments --------------------------------------------------------------------

def get_args():
    """
    Command line argument handling
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description="""processmedia2 migrate from processmedia1
        Migrate the old processmedia source data to processmedia2 path.
        Remove the nested folder structure
        Normalise tag filesnames with source filenames.

        This sould be run after scan_media.
        This should only need to be run once. Ever.
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

    #postmortem(migrate_media, **args)
    migrate_media(**args)
