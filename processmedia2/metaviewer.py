#!_env/bin/python3

import os
import re
from collections import defaultdict, namedtuple

from libs.misc import flatten  #  postmortem,

from processmedia_libs import add_default_argparse_args
from processmedia_libs.meta_manager import MetaManager, FileItemWrapper
from processmedia_libs.processed_files_manager import ProcessedFilesManager

import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'


# Meta info gatherer -----------------------------------------------------------

FileItem = namedtuple('FileItem', ('type', 'relative', 'absolute', 'exists'))


class MetaViewer(object):

    def __init__(self, path_meta=None, path_processed=None, path_source=None, **kwargs):
        self.fileitem_wrapper = FileItemWrapper(path_source)
        self.meta = MetaManager(path_meta)
        self.processed_files_manager = ProcessedFilesManager(path_processed)

    def get_meta_details(self, name_regex):
        if (not name_regex):
            self.meta.load_all()
            meta_items = self.meta.meta.values()
        else:
            meta_items = (
                self.meta.load(f.file_no_ext) or self.meta.get(f.file_no_ext)
                for f in self.meta.files
                if re.search(name_regex, f.file_no_ext, flags=re.IGNORECASE)
            )

        def lazy_exists(path):
            return lambda: os.path.exists(path)

        file_details = defaultdict(list)
        for m in meta_items:
            for f in filter(None, (f for f in self.fileitem_wrapper.wrap_scan_data(m).values())):
                file_details[m.name].append(FileItem('source', f['relative'], f['absolute'], lazy_exists(f['absolute'])))
            for f in flatten(self.processed_files_manager.get_all_processed_files_associated_with_source_hash(m.source_hash).values()):
                file_details[m.name].append(FileItem('processed', f.relative, f.absolute, lazy_exists(f.absolute)))

        return file_details


# Printed Output ---------------------------------------------------------------

class tcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'

class terminal:
    INDENTATION = '    '
    OK = tcolors.OKGREEN + '✔' + tcolors.ENDC
    FAIL = tcolors.FAIL + '✘' + tcolors.ENDC


def print_formated(file_details, **kwargs):
    def print_file(file_detail):
        print('{indendation}{filename} {exists}'.format(indendation=terminal.INDENTATION, filename=file_detail.relative, exists=(terminal.OK if file_detail.exists() else terminal.FAIL)))

    for title, files in file_details.items():
        print(tcolors.BOLD + title + tcolors.ENDC)
        for f in files:
            print_file(f)

# Arguments --------------------------------------------------------------------

def get_args():
    """
    Command line argument handling
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description="""processmedia2 metaviewer
        """,
        epilog="""
        """
    )

    add_default_argparse_args(parser)

    parser.add_argument('name_regex', default='', help='regex for names')
    #parser.add_argument('--hidesource', action='store_true')
    #parser.add_argument('--hideprocessed', action='store_true')
    #parser.add_argument('--raw', action='store_true')
    #parser.add_argument('--pathstyle', choices=('relative', 'absolute'), default='relative')

    args_dict = vars(parser.parse_args())

    return args_dict


if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=args['log_level'])

    metaviewer = MetaViewer(**args)
    print_formated(
        metaviewer.get_meta_details(args['name_regex'])
    )
