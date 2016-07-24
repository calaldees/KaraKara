import os

from processmedia_libs.meta_overlay import MetaManagerExtended

import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'


# Main -------------------------------------------------------------------------


def cleanup_media(**kwargs):
    meta_manager = MetaManagerExtended(**kwargs)
    meta_manager.load_all()

    all_known_file_hashs = {
        processed_file.hash
        for m in meta_manager.meta_items
        for processed_file in m.processed_files.values()
    }
    unlinked_files = (f for f in meta_manager.processed_files_manager.scan if f.file_no_ext and f.file_no_ext not in all_known_file_hashs)

    # Todo .. have dryrun and say how much this is cleaning up
    for unlinked_file in unlinked_files:
        os.remove(unlinked_file.absolute)


# Main -------------------------------------------------------------------------

if __name__ == "__main__":
    from _main import main
    main('cleanup_media', cleanup_media, version=VERSION)
