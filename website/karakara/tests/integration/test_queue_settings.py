import tempfile

from . import get_settings


def test_queue_settings(app, queue):
    key = 'karakara.test_setting'

    def _get_settings():
        return get_settings(app, queue)
    def _put_settings(data):
        app.put(f'/queue/{queue}/settings.json', data)

    # Settings API
    settings = _get_settings()
    assert settings
    assert key not in settings

    # Settings permissions
    # This is difficult to test as settings endpoint in test mode does not throw a 403
    #response = app.put('/settings.json', {key: 'bob'}, expect_errors=True)
    #assert response.status_code == 403
    #with admin_rights(app):
    _put_settings({key: 'bob'})
    assert _get_settings()[key] == 'bob'
    #_put_settings({key: '666 -> int'})
    #assert _get_settings()[key] == 666
    _put_settings({key: '665'})
    assert _get_settings()[key] == '665'
    _put_settings({key: '[]'})
    assert _get_settings()[key] == []


def test_queue_settings_template(app, queue):
    # Settings Template
    response = app.get(f'/queue/{queue}/settings')
    assert 'setting' in response.text.lower()
