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
    app.put('/settings.json', {key: '665'})
    assert get_settings(app)[key] == 665
    app.put('/settings.json', {key: '[]'})
    assert get_settings(app)[key] == []

    # Settings Template
    response = app.get('/settings')
    assert 'setting' in response.text.lower()
