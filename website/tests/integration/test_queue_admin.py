import pytest

from . import temporary_settings, admin_rights


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

        with admin_rights(app, queue):
            response = app.get('/')
            assert 'test menu disbaled' not in response.text


def test_queue_readonly_mode(app, queue, tracks):
    track_url = f'/queue/{queue}/track/t1'
    track_form_identifier = "form action='/queue"

    response = app.get(track_url)
    assert track_form_identifier in response.text

    with temporary_settings(app, queue, {'karakara.system.user.readonly': True}):

        # Normal users are restricted
        response = app.get(track_url)
        assert track_form_identifier not in response.text

        response = app.post(f'/queue/{queue}/queue_items', dict(track_id='t1', performer_name='bob'), status=403)
        assert 'readonly' in response.text

        # Admin users function as normal
        with admin_rights(app, queue):
            response = app.get(track_url)
            assert track_form_identifier in response.text
            # TODO - we need a way of adding to the queue and getting the queue_item.id back in the response
            #        currently this is not possible as the commit happens at the transaction level automatically
            #response = app.post('/queue.json', dict(track_id='t1', performer_name='bob')).json['data']
            #assert False

    # TODO - test 'update' and 'delete'? - for now testing the decoration once (above) is light enough


def test_admin_toggle(app, queue):
    """
    Switch to admin mode
    check main menu for admin options
    """
    queue_url = f'/queue/{queue}'

    def _get_admin_status():
        return app.get(f'{queue_url}?format=json').json['identity']['admin']
    def _set_admin_status(enabled, password=queue):
        return app.get(f'{queue_url}/admin?password={password if enabled else ""}')

    assert not _get_admin_status()
    app.get(f'{queue_url}/admin?password=NOT_REAL', expect_errors=True)  # Attempt to authenticate with wrong password
    assert not _get_admin_status()

    response = _set_admin_status(True)
    assert 'admin' in response.text
    response = app.get(queue_url)
    for text in ['class="admin"']:
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


