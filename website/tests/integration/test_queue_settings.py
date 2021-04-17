import pytest


def test_queue_settings(app, queue):
    key = 'karakara.test_setting'

    def _get_settings():
        return app.get(f'/queue/{queue}/settings.json').json['data']['settings']
    def _put_settings(data):
        app.put(f'/queue/{queue}/settings.json', data)

    # Settings API
    settings = _get_settings()
    assert settings
    assert key not in settings
    # There are no passthrough settings any more
    # assert 'karakara.websocket.host' in settings, 'Some registry.settings should always propergate through to this output'

    # Settings permissions
    # This is difficult to test as settings endpoint in test mode does not throw a 403
    #response = app.put('/settings.json', {key: 'bob'}, status=403)
    #with admin_rights(app):
    _put_settings({key: 'bob'})
    assert _get_settings()[key] == 'bob'
    #_put_settings({key: '666 -> int'})
    #assert _get_settings()[key] == 666
    _put_settings({key: '665'})
    assert _get_settings()[key] == '665'
    _put_settings({key: '[]'})
    assert _get_settings()[key] == []


def test_queue_settings_performers(app, queue):

    # TODO: These convenience methods are copy and pasted from the test above - unify them in some way
    def _get_settings():
        return app.get(f'/queue/{queue}/settings.json').json['data']['settings']
    def _put_settings(data):
        app.put(f'/queue/{queue}/settings.json', data)

    performers = ['bob', 'skull&crossbones', 'jane']
    _put_settings({'karakara.queue.add.valid_performer_names': ','.join(performers)})
    assert _get_settings()['karakara.queue.add.valid_performer_names'] == performers

    performers = []
    _put_settings({'karakara.queue.add.valid_performer_names': ','.join(performers)})
    assert _get_settings()['karakara.queue.add.valid_performer_names'] == performers


@pytest.mark.skip()
def test_queue_settings_with_json_data(app, queue):
    # TODO: we need to test content:"text/json" form submissions, as these handle json lists in a differnt way
    pass


def test_queue_settings_template(app, queue):
    # Settings Template
    response = app.get(f'/queue/{queue}/settings')
    assert 'setting' in response.text.lower()
