from collections import ChainMap

#from karakara.tests.data.tracks_random import random_tracks  # TODO Remove this file completely?
from karakara.model import init_DBSession, DBSession, commit
from karakara.model.model_tracks import Track
from karakara.model.actions import get_track, get_tag

import logging
log = logging.getLogger(__name__)


VERSION = 0.0

DEFAULT_TAGS = {
    'vocaltrack': 'band',
}

def band_tracks(DBSession, commit):

    data = [
        {
            'id': 'go',
            'tags': {
                'title': 'Go!!!',
                'category': 'anime',
                'from': 'Naruto',
                'artist': 'Flow',
                'lang': 'jp',
                'use': 'opening',
            },
        },
        {
            'id': 'power_rangers',
            'tags': {
                'title': 'Go Go Power Rangers',
                'category': 'cartoon',
                'from': 'Mighty Morphing Power Rangers',
                'lang': 'en',
                'artist': 'Ron Wasserman',
            },
        },
        {
            'id': 'reignite',
            'tags': {
                'title': 'Reignite',
                'category': 'game',
                'from': 'Mass Effect',
                'lang': 'en',
                'use': 'cover',
                'artist': 'Malukah',
            },
        },
        {
            'id': 'alchemy',
            'tags': {
                'title': 'Alchemy',
                'category': 'anime',
                'from': 'Angel Beats',
                'use': 'insert',
                'artist': 'Girls Dead Monster',
                'lang': 'jp',
            },
        },
        {
            'id': 'god_knows',
            'tags': {
                'title': 'God Knows',
                'category': 'anime',
                'from': 'The Melancholy of Haruhi Suzumiya',
                'artist': 'Satoru Kosaki',
                'lang': 'jp',
            }
        },
        {
            'id': 'lagann',
            'tags': {
                'title': 'Sorairo Days',
                'category': 'anime',
                'from': 'Gurren Lagann',
                'artist': 'Iwasaki Taku',
                'lang': 'jp',
                'use': 'opening',
            }
        },
    ]

    for d in data:
        _id = "band_{0}".format(d['id'])

        track = get_track(_id)
        if not track:
            track = Track()
            track.id = _id
            track.duration = 300
            track.tags = [get_tag(tag, parent=parent, create_if_missing=True) for parent, tag in ChainMap(d['tags'], DEFAULT_TAGS).items()]
            #track.attachments = attachments
            DBSession.add(track)

    commit()



def get_args():
    import argparse
    # Command line argument handling
    parser = argparse.ArgumentParser(
        description="""Insert band tracks into DB""",
        epilog=""""""
    )
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
    band_tracks(DBSession, commit)


if __name__ == "__main__":
    main()
