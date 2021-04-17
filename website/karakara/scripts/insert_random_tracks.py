#from karakara.tests.data.tracks_random import random_tracks  # TODO: Remove this file completely?
from karakara.model import init_DBSession, DBSession, commit

import logging
log = logging.getLogger(__name__)


VERSION = 0.0


#-------------------------------------------------------------------------------
# Command Line
#-------------------------------------------------------------------------------

def get_args():
    import argparse
    # Command line argument handling
    parser = argparse.ArgumentParser(
        description="""Insert random tracks into DB""",
        epilog=""""""
    )
    parser.add_argument('num_tracks', help='number of random tracks to generate', default=100, type=int)
    parser.add_argument('--config_uri', help='config .ini file for logging configuration', default='development.ini')
    parser.add_argument('--version', action='version', version=VERSION)

    return parser.parse_args()


def main():
    args = get_args()

    # Setup Logging and Db from .ini
    from pyramid.paster import get_appsettings  # , setup_logging
    #setup_logging(args.config_uri)
    logging.basicConfig(level=logging.INFO)
    settings = get_appsettings(args.config_uri)

    # Connect to DB
    init_DBSession(settings)
    #init_db()

    # Insert tracks
    random_tracks(None, DBSession, commit, args.num_tracks)


if __name__ == "__main__":
    main()
