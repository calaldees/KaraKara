import pytest

from .test_comunity import login, logout


def test_comunity_queue(app, queue, users):
    response = app.get('/comunity/queues', expect_errors=True)
    assert response.status_code == 403

    login(app)

    QUEUE_NEW = 'queue_new'
    response = app.get('/comunity/queues')
    assert queue in response.text
    assert QUEUE_NEW not in response.text

    response = app.post('/comunity/queues', {'id': QUEUE_NEW, 'format': 'redirect'})
    response = app.get('/comunity/queues')
    assert queue in response.text
    assert QUEUE_NEW in response.text

    response = app.get(f'/comunity/queues?method=delete&format=redirect&queue.id={QUEUE_NEW}')
    response = app.get('/comunity/queues')
    assert queue in response.text
    assert QUEUE_NEW not in response.text

    logout(app)