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


@pytest.mark.parametrize(('track_dict', 'expected_status', 'expected_statuss', 'expected_messages'), [
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

    # Default recomendations/warnings
    (
        {
            'tags': {
            },
        },
        'red',
        ('red', 'yellow'),
        ('title', 'artist'),
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
        ('artist'),
    ),

    # attachments

    # lyrics

])
def test_track_status(track_dict, expected_status, expected_statuss, expected_messages, func_is_file=None):
    status_dict = ComunityTrack.track_status(track_dict, status_tags=STATUS_TAGS)
    assert status_dict['status'] == expected_status
    for expected_status_key in expected_statuss:
        assert expected_status_key in status_dict['status_details']
    messages = "\n".join(map(str, status_dict['status_details'].values()))
    for message in expected_messages:
        assert message in messages
