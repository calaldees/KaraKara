import pytest


def test_queue_home_disabled(app, queue):
    """
    Menu has - a lightweight menu message diabler:
    In the event of load affecting the presentation screen we want a
    lightweight way to diable the system and inform users.
    We still want the system to operate for admins.
    Rather than locking down everthing venomusly, we can just disable the main menu.
    This will inform most users and throttle most traffic.
    """
    url_queue_home = f'/queue/{queue}'

    response = app.get(url_queue_home)
    assert 'test menu disbaled' not in response.text

    with temporary_settings(app, queue, {'karakara.template.menu.disable': 'test menu disbaled'}):
        response = app.get(url_queue_home)
        assert 'test menu disbaled' in response.text

        # TODO: Reimplement admin
        #response = app.get('/admin')
        #response = app.get('/')
        #assert 'test menu disbaled' not in response.text
        #response = app.get('/admin')


# TODO: Update this test
def test_queue_readonly_mode(app, tracks):
    response = app.get('/track/t1')
    assert "form action='/queue" in response.text

    response = app.put('/settings', {
        'karakara.system.user.readonly': 'True -> bool',
    })

    # Normal users are restricted
    response = app.get('/track/t1')
    assert "form action='/queue" not in response.text

    response = app.post('/queue', dict(track_id='t1', performer_name='bob'), expect_errors=True)
    assert response.status_code == 403
    assert 'readonly' in response.text

    # Admin users function as normal
    response = app.get('/admin')
    response = app.get('/track/t1')
    assert "form action='/queue" in response.text
    # TODO - we need a way of adding to the queue and getting the queue_item.id back in the response
    #        currently this is not possible as the commit happens at the transaction level automatically
    #response = app.post('/queue.json', dict(track_id='t1', performer_name='bob')).json['data']
    #assert False
    response = app.get('/admin')

    # TODO - test 'update' and 'delete'? - for now testing the decoration once (above) is light enough

    response = app.put('/settings', {
        'karakara.system.user.readonly': 'False -> bool',
    })


def test_admin_toggle(app, queue):
    """
    Switch to admin mode
    check main menu for admin options
    """
    queue_url = f'/queue/{queue}'

    def _get_admin_status():
        return app.get(f'{queue_url}?format=json').json['identity']['admin']
    def _set_admin_status(enabled):
        return app.get(f'{queue_url}/admin?password={queue if enabled else ""}', expect_errors=not enabled)

    assert not _get_admin_status()

    response = _set_admin_status(True)
    assert 'admin' in response.text
    response = app.get(queue_url)
    for text in ['Exit Admin Mode']:
        assert text in response.text
    response = _set_admin_status(False)

    assert not _get_admin_status()


@pytest.mark.skip()
def test_admin_lock(app):
    """
    TODO:
    Password can be set to '' and no further admins can be activated.
    """
    assert False


