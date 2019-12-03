## -*- coding: utf-8 -*-

import pytest
import random
from collections import namedtuple

from calaldees.string_tools import random_string

from karakara.model import DBSession, commit
from karakara.model.actions import get_tag
from karakara.model.model_tracks import Track, Attachment, Tag

AttachmentDescription = namedtuple('AttachmentDescription', ('location', 'type'))


def create_attachment(attachment_description):
    attachment = Attachment()
    attachment.location = attachment_description.location
    attachment.type = attachment_description.type
    DBSession.add(attachment)
    return attachment


@pytest.fixture(scope="session")
def tags(request):
    """
    Basic category tags for 3 test series
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
    assert DBSession.query(Tag).filter(Tag.name=='from').count() == 1, 'get_tag() should have found a single `from` tag'
    return tags


@pytest.fixture(scope="session")
def attachments(request):
    """
    Mock attachments
    """
    attachments_data = (
        AttachmentDescription('test/preview1.3gp', 'preview'),
        AttachmentDescription('test/preview2.flv', 'preview'),
        AttachmentDescription('test/preview3.mp4', 'preview'),
        AttachmentDescription('test/image1.jpg', 'image'),
        AttachmentDescription('test/image2.jpg', 'image'),
        AttachmentDescription('test/image3.png', 'image'),
        AttachmentDescription('test/processed.mpg', 'video'),
        AttachmentDescription('test/subtitles.srt', 'srt'),
    )
    mock_attachments = tuple(create_attachment(attachment) for attachment in attachments_data)

    def finalizer():
        pass
        #for attachment in attachments:
        #    DBSession.delete(attachment)
        #commit()
    request.addfinalizer(finalizer)

    commit()
    return mock_attachments


@pytest.fixture(scope="session")
def tracks(request, DBSession, commit, tags, attachments, cache_store):
    """
    4 test tracks with various unicode characters, lyrics, attachments, tags
    """
    tracks_data = [
        {
            'id': "t1",
            'duration': 60,  # 1min
            'tags': [
                'title      :Test Track 1',
                #'description:Test track for the KaraKara system with キ',
                'opening', 'male', 'jp', 'category:anime', 'category:jpop', 'series X',
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
                'ending', 'female', 'en', 'category:anime', 'series X',
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

    mock_tracks = tuple(create_test_track(**track_data) for track_data in tracks_data)  # Keep tabs on all tracks generated

    def finalizer():
        pass
        #for track in tracks:
        #    DBSession.delete(track)
        #commit()
    request.addfinalizer(finalizer)

    commit()
    cache_store.invalidate()
    return mock_tracks


@pytest.fixture(scope="function")
def tracks_volume(request, cache_store):
    """
    Create 15 random tracks to assert larger list
    """
    mock_tracks = tuple(create_test_track(tags=['test']) for track_num in range(15))

    def finalizer():
        for track in mock_tracks:
            DBSession.delete(track)
        commit()
    request.addfinalizer(finalizer)

    commit()
    cache_store.invalidate()
    return mock_tracks


def create_test_track(id=None, duration=None, tags=(), attachments=(), lyrics=None, source_filename=None):

    def _get_tag(tag):
        return get_tag(tag, create_if_missing=True)

    def _get_attachment(attachment):
        if hasattr(attachment, 'location') and hasattr(attachment, 'type'):
            return create_attachment(attachment)
        else:
            return DBSession.query(Attachment).filter(Attachment.location.like('%%{0}%%'.format(attachment))).one()

    track = Track()
    track.id = id if id else random_string(10)
    track.duration = duration if duration else random.randint(60, 360)
    for tag in tags:
        track.tags.append(_get_tag(tag))
    for attachment in attachments:
        track.attachments.append(_get_attachment(attachment))
    track.lyrics = lyrics or ''
    track.source_filename = source_filename

    DBSession.add(track)

    return track



@pytest.yield_fixture
def track_unicode_special(DBSession, commit):
    tags_data = (
        'title:UnicodeAssention',
        'from:Hack//Sign',
        'artist:こ',
    )
    def _create_tag(tag_data):
        tag = get_tag(tag_data, create_if_missing=True)
        DBSession.add(tag)
        return tag
    tag_objs = tuple(_create_tag(tag) for tag in tags_data)
    commit()

    track = Track()
    track.id = 'x999'
    track.duration = 120
    track.tags[:] = tag_objs
    track.source_filename = 'unicode_special'

    DBSession.add(track)
    commit()

    yield track

    DBSession.delete(track)
    for tag_obj in tag_objs:
        DBSession.delete(tag_obj)
    commit()
