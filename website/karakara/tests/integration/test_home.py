

def test_home(app):
    response = app.get('/')
    assert response.status_code == 200
    assert 'html' in response.content_type
    for text in ['KaraKara', 'jquery.mobile', 'queue_id', 'mobile.home.input_queue_label']:
        assert text in response.text


def test_home_queue_not_exists_redirect(app):
    response = app.get('/?queue_id=not_a_queue')
    assert response.status_code == 302
    response = response.follow()
    assert response.status_code == 302
    response = response.follow()
    assert 'view.queue.not_exist' in response.text
    assert 'not_a_queue' in response.text
