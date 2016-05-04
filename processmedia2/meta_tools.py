import os
import operator
import re
from collections import defaultdict, namedtuple

from libs.misc import postmortem, flatten

from processmedia_libs import add_default_argparse_args
from processmedia_libs.meta_manager import MetaManager, FileItemWrapper
from processmedia_libs.processed_files_manager import ProcessedFilesManager

import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'

FileItem = namedtuple('FileItem', ('type', 'relative', 'absolute', 'exists'))

# Main -------------------------------------------------------------------------


def meta_tools(name_regex=None, **kwargs):
    file_details = get_file_details(name_regex, kwargs['path_source'], kwargs['path_meta'], kwargs['path_processed'])


def get_file_details(name_regex, path_source, path_meta, path_processed):
    fileitem_wrapper = FileItemWrapper(path_source)
    meta = MetaManager(path_meta)
    processed_files_manager = ProcessedFilesManager(path_processed)

    if (not name_regex):
        meta.load_all()
        meta_items = meta.meta.values()
    else:
        meta_items = (
            meta.load(f.file_no_ext) or meta.get(f.file_no_ext)
            for f in meta.files
            if re.search(name_regex, f.file_no_ext, flags=re.IGNORECASE)
        )

    file_details = defaultdict(list)
    for m in meta_items:
        for f in filter(None, (f for f in fileitem_wrapper.wrap_scan_data(m).values())):
            file_details[m.name].append(FileItem('source', f['realtive'], f['absolute'], lambda: os.path.exists(f['absolute'])))
        for f in flatten(processed_files_manager.get_all_processed_files_associated_with_source_hash(m.source_hash).values()):
            file_details[m.name].append(FileItem('processed', f.relative, f.absolute, lambda: os.path.exists(f.absolute)))
    return file_details


def print_formated(file_details, **kwargs):
    def print_files(files, indentation='  '):
        for f in files:
            print('{}{}'.format(indentation, f))

    #indentation = ''
    #if kwargs.get('pretty'):
        #print(m.name)
    #    indentation = '  '
    #if kwargs.get('showsource'):
        #print_files(source_files, indentation)
    #if kwargs.get('showprocessed'):
    #    print_files(processed_files, indentation)

    #if kwargs.get('pretty'):
    #    print()



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
    parser.add_argument('--hidesource', action='store_true')
    parser.add_argument('--hideprocessed', action='store_true')
    parser.add_argument('--raw', action='store_true')
    parser.add_argument('--pathstyle', choices=('relative', 'absolute'), default='relative')

    args_dict = vars(parser.parse_args())

    return args_dict


if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=args['log_level'])

    postmortem(meta_tools, **args)
