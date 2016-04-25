import os
import operator
import re

from libs.misc import postmortem, flatten

from processmedia_libs import add_default_argparse_args
from processmedia_libs.meta_manager import MetaManager, FileItemWrapper
from processmedia_libs.processed_files_manager import ProcessedFilesManager

import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'


# Main -------------------------------------------------------------------------


def meta_tools(name_regex=None, **kwargs):
    fileitem_wrapper = FileItemWrapper(kwargs['path_source'])
    processed_files_manager = ProcessedFilesManager(kwargs['path_processed'])
    meta = MetaManager(kwargs['path_meta'])

    if (not name_regex):
        meta.load_all()
        meta_items = meta.meta.values()
    else:
        meta_items = (meta.load(f.file_no_ext) or meta.get(f.file_no_ext) for f in meta.files if re.search(name_regex, f.file_no_ext, flags=re.IGNORECASE))

    path_attrgetter = operator.attrgetter(kwargs['pathstyle'])
    path_itemgetter = operator.itemgetter(kwargs['pathstyle'])

    def print_files(files, indentation='  '):
        for f in files:
            print('{}{}'.format(indentation, f))

    for m in meta_items:
        indentation = ''
        if kwargs.get('pretty'):
            print(m.name)
            indentation = '  '
        if kwargs.get('showsource'):
            source_files = (
                path_itemgetter(f) for f in fileitem_wrapper.wrap_scan_data(m).values() if f
            )
            print_files(source_files, indentation)
        if kwargs.get('showprocessed'):
            processed_files = (
                path_attrgetter(f) for f in flatten(
                    processed_files_manager.get_all_processed_files_associated_with_source_hash(m.source_hash).values()
                )
            )
            print_files(processed_files, indentation)
        if kwargs.get('pretty'):
            print()


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

    parser.add_argument('name_regex', default='', help='regex for names')
    parser.add_argument('--showsource', action='store_true')
    parser.add_argument('--showprocessed', action='store_true')
    parser.add_argument('--pretty', action='store_true')
    parser.add_argument('--pathstyle', choices=('relative', 'absolute'), default='relative')

    args_dict = vars(parser.parse_args())

    return args_dict


if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=args['log_level'])

    postmortem(meta_tools, **args)
