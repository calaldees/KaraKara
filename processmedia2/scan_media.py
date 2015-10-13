import re

from libs.misc import postmortem, file_extension_regex
from libs.file import FolderStructure

from processmedia_libs.scan import locate_primary_files, get_file_collection, ALL_EXTS, PRIMARY_FILE_RANKED_EXTS
from processmedia_libs.meta_manager import MetaManager

import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'
DEFAULT_PATH_SOURCE = '../mediaserver/www/files/'
DEFAULT_PATH_PROCESSED = '../mediaserver/www/processed/'
DEFAULT_PATH_META = '../mediaserver/www/meta/'


# Protection for legacy processed files  (could be removed in once data fully migriated)
DEFAULT_IGNORE_FILE_REGEX = re.compile(r'0\.mp4|0_generic\.mp4|\.bak|^\.|^0_video\.|0_\d\.jpg')

IGNORE_SEARCH_EXTS_REGEX = file_extension_regex(('txt', ))

# Main -------------------------------------------------------------------------

def main(**kwargs):
    """
    part 1 of 3 of the encoding system

    SCAN
        -Update Meta-
        Load meta
        validate source meta files
            check mtime (ok or->)
            check hash
            mark fail if needed
        scan source
            skip validated
            scan hash in attempt to match failed
        create meta stubs for new files
        remove old failed bits of meta

        -Add jobs-
            update tags
            extract lyrics
            check source->destination hashs and add to job list


    """
    meta = MetaManager(kwargs['path_meta'])
    meta.load_all()

    # 1.) Read file structure into memory
    folder_structure = FolderStructure.factory(
        kwargs['path_source'],
        file_regex=file_extension_regex(ALL_EXTS),
        ignore_regex=DEFAULT_IGNORE_FILE_REGEX
    )

    # 2.) Locate primary files
    primary_files = locate_primary_files(folder_structure, file_regex=file_extension_regex(PRIMARY_FILE_RANKED_EXTS))

    # 3.) Find associated files as a 'file collection' (based on the name of the primary file)
    file_collections = {
        f.file_no_ext: get_file_collection(folder_structure, f)
        for f in primary_files
    }

    # 4.) Associate file_collections with existing metadata objects
    for name, file_collection in file_collections.items():
        meta.get(name).associate_file_collection(file_collection)

    # 5.) Attempt to find associate unassociated files but finding them on the folder_structure in memory
    for m in meta.meta_with_unassociated_files:
        for filename, scan_data in m.unassociated_files.items():

            # 5a.) The unassociated file may not have been found in the inital collection scan,
            # check it's original location and associate if it exists
            f = folder_structure.get(scan_data.get('relative')) if scan_data.get('relative') else None
            if f:
                m.associate_file(f)
                log.warn('Associating found missing file %s to %s - this should not be a regular occurance, move/rename this so it is grouped effectivly', f.relative, m.name)
                continue

            # 5b.) Search the whole folder_structure in memory for a matching hash
            mtime = scan_data['mtime']
            for f in folder_structure.scan(
                lambda f:
                    not IGNORE_SEARCH_EXTS_REGEX.search(f.file)
                    and
                    (f.file == filename or f.stats.st_mtime == mtime)
                    and
                    str(f.hash) == scan_data['hash']
            ):
                log.warn('Associating found missing file %s to %s - this should not be a regular occurance, move/rename this so it is grouped effectivly', f.relative, m.name)
                m.associate_file(f)
                break

    # 6.) Remove unmatched meta entrys
    # (If processed data already exisits, it will be relinked at the encode level)
    for name in [m.name for m in meta.unmatched_entrys]:
        log.info('Removing meta %s', m.name)
        meta.delete(m.name)

    meta.save_all()


# Arguments --------------------------------------------------------------------

def get_args():
    """
    Command line argument handling
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description="""processmedia
        """,
        epilog="""
        """
    )
    parser_input = parser

    parser_input.add_argument('--path_source', action='store', help='', default=DEFAULT_PATH_SOURCE)
    parser_input.add_argument('--path_processed', action='store', help='', default=DEFAULT_PATH_PROCESSED)
    parser_input.add_argument('--path_meta', action='store', help='', default=DEFAULT_PATH_META)

    parser.add_argument('--log_level', type=int, help='log level', default=logging.INFO)
    parser.add_argument('--version', action='version', version=VERSION)

    args = vars(parser.parse_args())

    return args


if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=args['log_level'])

    postmortem(main, **args)
