import tempfile

from . import get_settings


def test_settings(app):
    key = 'karakara.test_setting'

    # Settings API
    settings = get_settings(app)
    assert settings
    assert key not in settings

    # Settings permissions
    # This is difficult to test as settings endpoint in test mode does not throw a 403
    #response = app.put('/settings.json', {key: 'bob'}, expect_errors=True)
    #assert response.status_code == 403
    #with admin_rights(app):
    app.put('/settings.json', {key: 'bob'})
    assert get_settings(app)[key] == 'bob'
    app.put('/settings.json', {key: '666 -> int'})
    assert get_settings(app)[key] == 666
    app.put('/settings.json', {key: '[]'})
    assert get_settings(app)[key] == []

    with tempfile.NamedTemporaryFile(mode='w') as temp:
        # Setup actual file on filesystem as a list
        users = ('user1', 'user2', 'mysteryman')
        for user in users:
            temp.write('{0}\n'.format(user))
        temp.flush()

        # Assert the file can be read by ->listfile
        app.put('/settings.json', {key: '{0} -> listfile'.format(temp.name)})
        assert isinstance(get_settings(app)[key], list)
        for user in users:
            assert user in get_settings(app)[key]

        # Just so that you know that I know.
        # This settings feature could be a security hole
        # Any file can be ready and put into settings
        # But only admins can change settings ... so ... maybe not that problematic

    # Settings Template
    response = app.get('/settings')
    assert 'setting' in response.text.lower()

