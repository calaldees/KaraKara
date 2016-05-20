import pytest

from karakara.views.comunity import ComunityTrack

STATUS_TAGS = {
    'required': ('title',),
    'recomended': ('artist',),
    'yellow': ('yellow', 'problem'),
    'red': ('red', 'broken'),
    'black': ('black', 'delete'),
    'green': ('green', 'ok')
}

@pytest.mark.xfail  # Temp during refactoring
@pytest.mark.parametrize(('track_dict', 'expected_status', 'expected_statuss', 'expected_messages'), [
    # Complete without warnings/errors
    (
        {
            'tags': {
                'title': ['test title'],
                'artist': ['test artist'],
            },
            'lyrics': [
                {'id': 1, 'lang': 'en', 'content': 'lyric test'}
            ],
            'duration': 100,
            'attachments': [
                {'location': '/test/test.jpg'}
            ],
        },
        None,
        (),
        (),
    ),

    # Default recomendations/warnings
    (
        {
            'tags': {
            },
        },
        'red',
        ('red', 'yellow'),
        ('title', 'artist', 'attachments', 'duration'),
    ),

    # Single green anonymous tag
    (
        {
            'tags': {
                None: ['test', 'test', 'green'],
            },
        },
        'green',
        ('green',),
        (),
    ),

    # Multi tag yellow, red
    (
        {
            'tags': {
                None: ['test', 'test', 'yellow', 'red'],
            },
        },
        'red',
        ('red', 'yellow'),
        (),
    ),

    # Multi tag black
    (
        {
            'tags': {
                'black': ['scheduled for removal', 'scheduled for death'],
            },
        },
        'black',
        ('black',),
        ('removal', 'death'),
    ),

    # Missing tags and explicit tags
    (
        {
            'tags': {
                'green': ['quality checked'],
                'title': ['test title'],
            },
        },
        'green',
        ('green', 'yellow'),
        ('artist',),
    ),

    # attachments
    # TODO
    #  currently func_is_file is not used. The default of 'True' is always present on the defaut implementation


    # lyrics missing is an error
    (
        {
            'tags': {
                'title': ['test title'],
                'artist': ['test artist'],
            },
            'duration': 100,
            'attachments': [
                {'location': '/test/test.jpg'}
            ],
        },
        'red',  # Unless explicity stated. Missing lyrics is a BAD thing for a karaoke system
        ('red',),
        ('lyrics',),
    ),
    # lyric - special case - remove lyric 'missing warning' if hardsubs anaonimus tag is used
    (
        {
            'tags': {
                'title': ['test title'],
                'artist': ['test artist'],
                None: ['hardsubs'],
            },
            'duration': 100,
            'attachments': [
                {'location': '/test/test.jpg'}
            ],
        },
        None,
        (),
        (),
    ),

])
def test_track_status(track_dict, expected_status, expected_statuss, expected_messages, func_is_file=None):
    status_dict = ComunityTrack.track_status(track_dict, status_tags=STATUS_TAGS)
    assert status_dict['status'] == expected_status
    for expected_status_key in expected_statuss:
        assert expected_status_key in status_dict['status_details']
    messages = "\n".join(map(str, status_dict['status_details'].values()))
    for message in expected_messages:
        assert message in messages
