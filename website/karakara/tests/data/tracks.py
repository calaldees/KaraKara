## -*- coding: utf-8 -*-

import pytest

from externals.lib.misc import random_string, random

from karakara.model import DBSession, commit
from karakara.model.actions import get_tag
from karakara.model.model_tracks import Track, Attachment

from karakara.views import cache


@pytest.fixture(scope="session")
def tags(request):
    """
    """
    tags_data = [
        'from:series X',
        'from:series Y',
        'from:series Z',
    ]
    tags = []
    for tag_data in tags_data:
        tag = get_tag(tag_data, create_if_missing=True)
        DBSession.add(tag)
        tags.append(tag)

    def finalizer():
        pass
        #for tag in tags:
        #    DBSession.delete(tag)
        #commit()
    #request.addfinalizer(finalizer)

    commit()
    return tags


@pytest.fixture(scope="session")
def attachments(request):
    """
    """
    attachments_data = (
        ('test/preview1.3gp', 'preview'),
        ('test/preview2.flv', 'preview'),
        ('test/preview3.mp4', 'preview'),
        ('test/image1.jpg', 'image'),
        ('test/image2.jpg', 'image'),
        ('test/image3.png', 'image'),
        ('test/processed.mpg', 'video'),
        ('test/subtitles.srt', 'srt'),
    )
    attachments = []
    for attachment_location, attachment_type in attachments_data:
        attachment = Attachment()
        attachment.location = attachment_location
        attachment.type = attachment_type
        DBSession.add(attachment)
        attachments.append(attachment)

    def finalizer():
        pass
        #for attachment in attachments:
        #    DBSession.delete(attachment)
        #commit()
    request.addfinalizer(finalizer)

    commit()
    return attachments


@pytest.fixture(scope="session")
def tracks(request, DBSession, commit, tags, attachments):
    tracks_data = [
        {
            'id': "t1",
            'duration': 60,  # 1min
            'tags': [
                'title      :Test Track 1',
                #'description:Test track for the KaraKara system with キ',
                'opening', 'male', 'jp', 'anime', 'jpop', 'series X',
            ],
            'attachments': ['image1', 'preview1', 'processed'],
            'lyrics': 'ここにいくつかのテキストです。',
            'source_filename': 'track1source',
        },
        {
            'id': "t2",
            'duration': 120,  # 2min
            'tags': [
                'title      :Test Track 2',
                #'description:Test track for the KaraKara system with キ'
                'ending', 'female', 'en', 'anime', 'series X',
            ],
            'attachments': ['image2', 'preview2'],
            'lyrics': 'Line1\nLine2\nLine3\nLine4\näöü"',
            'source_filename': 'track2source',
        },
        {
            'id': "t3",
            'duration': 240,  # 4min
            'tags':[
                'title      :Test Track 3 キ',
                #'description:Test track for the KaraKara system with キ',
                'ending', 'female', 'en', 'jpop', 'series Y',
            ],
            'attachments': ['image3', 'preview3'],
            'source_filename': 'track3source',
        },
        {
            'id': "xxx",
            'duration': 300,  # 5min
            'tags': [
                'title      :Wildcard',
                'lang:fr',
            ],
            'attachments': [],
            'source_filename': 'wildcardsource',
        },
    ]

    tracks = []  # Keep tabs on all tracks generated 
    for track_data in tracks_data:
        track = create_test_track(**track_data)
        DBSession.add(track)
        tracks.append(track)

    def finalizer():
        pass
        #for track in tracks:
        #    DBSession.delete(track)
        #commit()
    request.addfinalizer(finalizer)

    commit()
    cache.invalidate()
    return tracks


@pytest.fixture(scope="function")
def tracks_volume(request):
    tracks = [create_test_track(tags=['test']) for track_num in range(15)]
    [DBSession.add(track) for track in tracks]

    def finalizer():
        for track in tracks:
            DBSession.delete(track)
        commit()
    request.addfinalizer(finalizer)

    commit()
    cache.invalidate()
    return tracks


def create_test_track(id=None, duration=None, tags=[], attachments=[], lyrics=None, source_filename=None):
    def _get_tag(tag):
        return get_tag(tag, create_if_missing=True)
    def _get_attachment(filename):
        return DBSession.query(Attachment).filter(Attachment.location.like('%%{0}%%'.format(filename))).one()

    track = Track()
    track.id          = id       if id       else random_string(10)
    track.duration    = duration if duration else random.randint(60,360)
    [track.tags       .append(_get_tag       (t)) for t in tags       ]
    [track.attachments.append(_get_attachment(a)) for a in attachments]
    track.lyrics = lyrics or ''
    track.source_filename = source_filename
    return track
