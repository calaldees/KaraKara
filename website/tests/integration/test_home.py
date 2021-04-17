

def test_home(app):
    response = app.get('/', status=200)
    assert 'html' in response.content_type
    for text in ['KaraKara', 'jquery.mobile', 'queue_id', 'mobile.home.input_queue_label']:
        assert text in response.text


def test_home_queue_not_exists_redirect(app):
    response = app.get('/?queue_id=not_a_queue', status=302)
    response = response.follow(status=302)
    response = response.follow()
    assert 'view.queue.not_exist' in response.text
    assert 'not_a_queue' in response.text


def test_queue_home_exists_case_insensetive(app, queue):
    response = app.get(f'/?queue_id={queue.title()}', status=302)
    response = response.follow()
    assert response.request.path == f'/queue/{queue}'
    assert 'view.queue.not_exist' not in response.text
