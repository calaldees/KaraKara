import os

from functools import partial

from libs.misc import postmortem, file_extension_regex, fast_scan_regex_filter, flatten, first
from libs.file import FolderStructure

from processmedia_libs import ALL_EXTS

from scan_media import DEFAULT_IGNORE_FILE_REGEX

import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'

# Utils ------------------------------------------------------------------------

def move_func_mock(src, dest):
    log.debug('rename {0} -> {1}'.format(src, dest))
MOVE_FUNCTIONS = {
    'dryrun': move_func_mock,
    'move': shutil.move  #os.rename,  
    'link': os.symlink,
}


auto_categorys = {
    'Anime - ': 'Anime',
    'Import - ': '',
    'Cartoon - ': 'Cartoon',
    'Game - ': 'Game',
    'J-Pop - ': 'JPop',
    'JPop - ': 'JPop',
    'Jpop - ': 'JPop',
}
def auto_category(parent_folder):
    for parent_folder_prefix, auto_category_folder in auto_categorys.items():
        if parent_folder.startswith(parent_folder_prefix):
            return parent_folder.replace(parent_folder_prefix, ''), auto_category_folder
    return parent_folder, ''


# Main -------------------------------------------------------------------------


def migrate_media(move_func=MOVE_FUNCTIONS['dryrun'], **kwargs):
    # Read file structure into memory
    folder_structure = FolderStructure.factory(
        path=kwargs['path_source'],
        search_filter=fast_scan_regex_filter(
            file_regex=file_extension_regex(ALL_EXTS),
            ignore_regex=DEFAULT_IGNORE_FILE_REGEX,
        )
    )

    if move_func != MOVE_FUNCTIONS['dryrun']:
        for folder in auto_categorys.values():
            os.makedirs(os.path.join(kwargs['path_destination'], folder), exist_ok=True)

    for f in folder_structure.all_files:
        if f.folder.endswith('/source') or f.file == 'tags.txt':
            parent_folder, auto_category_folder = auto_category(first(os.path.split(f.folder)))
            dest = os.path.join(
                kwargs['path_destination'],
                auto_category_folder,
                '{0}.{1}'.format(parent_folder, f.ext)
            )
            if not os.path.exists(dest):
                move_func(f.abspath, dest)  # abspath is a temp botch, We need to fix .absolute in misc.py


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

    parser.add_argument('--path_destination', action='store', help='Destination for migrated files')
    parser.add_argument('--move_func', choices=MOVE_FUNCTIONS.keys(), help='method of migation', default='dryrun')

    args_dict = parse_args(parser)

    args_dict['move_func'] = MOVE_FUNCTIONS[args_dict['move_func']]

    return args_dict



if __name__ == "__main__":
    args = get_args()

    postmortem(migrate_media, **args)
    #migrate_media(**args)
