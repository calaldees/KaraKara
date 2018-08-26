import sys
import re
import operator

from calaldees.misc import postmortem, file_extension_regex, fast_scan_regex_filter
from calaldees.file import FolderStructure
from clint.textui.progress import bar as progress_bar

from processmedia_libs import ALL_EXTS
from processmedia_libs.scan import locate_primary_files, get_file_collection, PRIMARY_FILE_RANKED_EXTS
from processmedia_libs.meta_manager import MetaManager
from processmedia_calaldees.fileset_change_monitor import FilesetChangeMonitor

import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'


# Protection for legacy processed files  (could be removed in once data fully migriated)
DEFAULT_IGNORE_FILE_REGEX = re.compile(r'0\.mp4|0_generic\.mp4|\.bak|^\.|^0_video\.|0_\d\.jpg|sync-conflict|~\d{8}-\d{6}')

IGNORE_SEARCH_EXTS_REGEX = file_extension_regex(('txt', ))


# Main -------------------------------------------------------------------------

def scan_media(**kwargs):
    """
    """

    meta = MetaManager(kwargs['path_meta'])
    meta.load_all()

    log.info('1.) Read file structure into memory')
    folder_structure = FolderStructure.factory(
        path=kwargs['path_source'],
        search_filter=fast_scan_regex_filter(
            file_regex=file_extension_regex(ALL_EXTS),
            ignore_regex=DEFAULT_IGNORE_FILE_REGEX,
        )
    )

    log.info('2.) Locate primary files')
    # Note: Duplicate media is completely ignored/removed in this list
    primary_files = locate_primary_files(folder_structure, file_regex=file_extension_regex(PRIMARY_FILE_RANKED_EXTS))

    log.info("3.) Find associated files as a 'file collection' (based on the name of the primary file)")
    file_collections = {
        f.file_no_ext: get_file_collection(folder_structure, f)
        for f in primary_files
    }

    log.info('4.) Associate file_collections with existing metadata objects')
    for name, file_collection in progress_bar(file_collections.items()):
        meta.load(name)
        m = meta.get(name)
        for f in file_collection:
            m.associate_file(f)
        meta.save(name)

    log.info('5.) Attempt to find associate unassociated files but finding them on the folder_structure in memory')
    # TODO: The step in 5b (mtime and hash check) is not sufficent
    #   We need to identify all unmatched files and generate a hash lookup and match them that way.
    #   It may take longer but it's the only true way of matching a file.
    #   It might in some cases be quicker because we don't need to craw the entire file structure in memory.

    # These are meta items that have a filecollection matched,
    # but that file collection is incomplete, so we have some child files missing
    has_unassociated_files = operator.attrgetter('unassociated_files')
    for m in filter(has_unassociated_files, meta.meta.values()):
        for filename, scan_data in m.unassociated_files.items():

            # 5a.) The unassociated file may not have been found in the inital collection scan,
            # check it's original location and associate if it exists
            f = folder_structure.get(scan_data.get('relative')) if scan_data.get('relative') else None
            if f:
                m.associate_file(f)
                log.warning('Associating found missing file %s to %s - this should not be a regular occurance, move/rename this so it is grouped effectivly', f.relative, m.name)
                continue

            # 5b.) Search the whole folder_structure in memory for a matching hash
            mtime = scan_data['mtime']
            for f in folder_structure.scan(
                lambda f:
                    not IGNORE_SEARCH_EXTS_REGEX.search(f.file)
                    and
                    (f.file == filename or f.stats.st_mtime == mtime)  # TODO: Depricate this!
                    and
                    str(f.hash) == scan_data['hash']
            ):
                log.warning('Associating found missing file %s to %s - this should not be a regular occurance, move/rename this so it is grouped effectivly', f.relative, m.name)
                m.associate_file(f)
                break

        # 5c.)
        # We have done our best at locating missing files
        # Remove them from the tracked list of files.
        m.unlink_unassociated_files()

    log.info('6.) Remove unmatched meta entrys')
    for m in [m for m in meta.meta.values() if not m.file_collection]:
        log.info('Removing meta %s', m.name)
        meta.delete(m.name)

    # (If processed data already exisits, it will be relinked at the encode level)

    meta.save_all()


if __name__ == "__main__":
    from _main import main
    main('scan_media', scan_media, folder_type_to_derive_mtime='source', version=VERSION)
