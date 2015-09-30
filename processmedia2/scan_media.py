import processmedia_libs.file_manager as file_manager
import processmedia_libs.meta_manager as MetaManager

import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'
DEFAULT_PATH_SOURCE = '../mediaserver/www/files/'
DEFAULT_PATH_PROCESSED = '../mediaserver/www/processed/'
DEFAULT_PATH_META = '../mediaserver/www/meta/'


# Main -------------------------------------------------------------------------

def main():
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
    meta = MetaManager(DEFAULT_PATH_META)

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

    parser.add_argument('--log_level', type=int,  help='log level', default=logging.INFO)
    parser.add_argument('--version', action='version', version=VERSION)

    args = vars(parser.parse_args())

    return args


if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=args['log_level'])

    file_manager.source_file_generator(args['path_source'])
