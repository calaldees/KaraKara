import hashlib
import re
import os
import pickle

from externals.lib.misc import file_scan, update_dict

import logging
log = logging.getLogger(__name__)

VERSION = "0.0"

# Constants --------------------------------------------------------------------

DEFAULT_DESTINATION = './files/'
DEFAULT_CACHE_FILENAME = 'hash_cache.pickle'

DEFAULT_FILE_EXTS = {'mp4', 'avi', 'rm', 'mkv', 'ogm', 'ssa', 'srt', 'ass'}


# Utils ------------------------------------------------------------------------

def hash_files(source_folder=None, destination_folder=None, hasher=hashlib.sha256, file_exts=DEFAULT_FILE_EXTS, **kwargs):
    file_regex = re.compile(r'.*\.({})$'.format('|'.join(file_exts)))

    gen_hashs = lambda folder: {
        f.hash: f
        for f in file_scan(folder, file_regex=file_regex, hasher=hasher)
    }

    return {
        'source_files': gen_hashs(source_folder),
        'destination_files': gen_hashs(destination_folder),
    }


def match_files(source_files=None, destination_files=None, destination_folder=None, dry_run=False, **kwargs):
    for key in sorted(set(source_files.keys()).difference(set(destination_files.keys())), key=lambda key: source_files[key].file):
        f = source_files[key]
        log.debug(f.file)
        if not dry_run:
            try:
                os.symlink(f.absolute, os.path.join(destination_folder, f.file))
            except OSError:
                log.info('unable to symlink {0}'.format(f.file))


# Command Line -----------------------------------------------------------------

def get_args():
    import argparse
    parser = argparse.ArgumentParser(
        description="""
        Find the duplicates
        """,
        epilog=""" """
    )

    # Folders
    parser.add_argument('-d', '--destination_folder', action='store', help='', default=DEFAULT_DESTINATION)
    parser.add_argument('-s', '--source_folder', action='store', help='', required=True)

    parser.add_argument('-e', '--file_exts', nargs='*', help='file exts to find', default=DEFAULT_FILE_EXTS)

    # Operation
    parser.add_argument('-c', '--copy', action='store_true', help='copy files to destination (to be ready for importing)', default=False)

    # Cache
    parser.add_argument('--cache_filename', action='store', help='', default=DEFAULT_CACHE_FILENAME)

    # Common
    parser.add_argument('--dry_run', action='store_true', help='', default=False)
    parser.add_argument('-v', '--verbose', action='store_true', help='', default=False)
    parser.add_argument('--version', action='version', version=VERSION)

    args = vars(parser.parse_args())

    return args


def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args['verbose'] else logging.INFO)

    try:
        with open(args['cache_filename'], 'rb') as f:
            data = pickle.load(f)
    except IOError:
        with open(args['cache_filename'], 'wb') as f:
            data = hash_files(**args)
            pickle.dump(data, f)

    match_files(**update_dict(args.copy(), data))

if __name__ == "__main__":
    main()
