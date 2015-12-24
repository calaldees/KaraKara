from pprint import pprint

from libs.misc import postmortem

from processmedia_libs import add_default_argparse_args
from processmedia_libs.meta_manager import MetaManager

import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'


# Main -------------------------------------------------------------------------


def main(**kwargs):
    meta = MetaManager(kwargs['path_meta'])
    meta.load_all()

    for name, meta in meta.meta.items():
        import pdb ; pdb.set_trace()
        meta.scan_data


# Arguments --------------------------------------------------------------------

def get_args():
    """
    Command line argument handling
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description="""processmedia2 migrate
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

    postmortem(main, **args)
