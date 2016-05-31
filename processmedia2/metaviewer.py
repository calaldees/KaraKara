#!_env/bin/python3

import os
import re
from collections import defaultdict, namedtuple

from libs.misc import flatten

from processmedia_libs.meta_overlay import MetaManagerExtended


import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'


# Meta info gatherer -----------------------------------------------------------

FileItem = namedtuple('FileItem', ('type', 'relative', 'absolute', 'exists'))


class MetaViewer(object):

    def __init__(self, path_meta=None, path_processed=None, path_source=None, **kwargs):
        self.meta_manager = MetaManagerExtended(path_meta=path_meta, path_source=path_source, path_processed=path_processed)

    def get_meta_details(self, name_regex):
        if (not name_regex):
            self.meta_manager.load_all()
            meta_items = self.meta_manager.meta_items
        else:
            meta_items = (
                self.meta_manager.load(f.file_no_ext) or self.meta_manager.get(f.file_no_ext)
                for f in self.meta_manager.files
                if re.search(name_regex, f.file_no_ext, flags=re.IGNORECASE)
            )

        def lazy_exists(path):
            return lambda: os.path.exists(path)

        file_details = defaultdict(list)
        for m in meta_items:
            for f in filter(None, m.source_files.values()):
                file_details[m.name].append(FileItem('source', f['relative'], f['absolute'], lazy_exists(f['absolute'])))
            for f in m.processed_files.values():
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
        files = tuple(files)
        if not files:
            continue
        print(tcolors.BOLD + title + tcolors.ENDC)
        for f in files:
            print_file(f)

# Main -------------------------------------------------------------------------


def additional_arguments(parser):
    parser.add_argument('name_regex', default='', help='regex for names')
    parser.add_argument('--hidesource', action='store_true')
    parser.add_argument('--hideprocessed', action='store_true')
    parser.add_argument('--showmissing', action='store_true')
    #parser.add_argument('--raw', action='store_true')
    #parser.add_argument('--pathstyle', choices=('relative', 'absolute'), default='relative')


def _metaviewer(*args, **kwargs):
    metaviewer = MetaViewer(*args, **kwargs)
    file_details = metaviewer.get_meta_details(kwargs['name_regex'])
    if kwargs.get('showmissing'):
        file_details = {k: filter(lambda f: not f.exists(), v) for k, v in file_details.items()}
    print_formated(file_details)


if __name__ == "__main__":
    from _main import main
    main(
        'metaviewer', _metaviewer, version=VERSION,
        additional_arguments_function=additional_arguments,
    )
