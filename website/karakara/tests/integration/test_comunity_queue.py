import pytest

from .test_comunity import login, logout

from karakara.model.model_queue import QueueItem

def test_comunity_queue(app, queue, users, tracks, DBSession):
    response = app.get('/comunity/queues', expect_errors=True)
    assert response.status_code == 403

    login(app)

    QUEUE_NEW = 'queue_new'

    response = app.get('/comunity/queues')
    for text in {queue, 'player', 'track_list', 'settings', 'badgenames', 'password'}:
        # todo: could use soup to check for links
        assert queue in response.text
    assert QUEUE_NEW not in response.text

    response = app.post('/comunity/queues', {'queue_id': QUEUE_NEW.title(), 'queue_password': 'bad'}, expect_errors=True)
    assert response.status_code == 400
    assert 'uppercase' in response.text.lower()

    response = app.post('/comunity/queues', {'queue_id': QUEUE_NEW, 'format': 'redirect'}, expect_errors=True)
    assert response.status_code == 302
    response = response.follow()
    #assert response.status_code == 400  # This is a normal page load with a flash message
    assert 'api.error.param_required' in response.text

    response = app.post('/comunity/queues', {'queue_id': QUEUE_NEW, 'queue_password': 'password', 'format': 'redirect'})

    response = app.get('/comunity/queues')
    assert queue in response.text
    assert QUEUE_NEW in response.text

    # Add a track to the queue
    def tracks_queued_count():
        return DBSession.query(QueueItem).filter(QueueItem.queue_id == QUEUE_NEW).count()
    response = app.post(f'/queue/{QUEUE_NEW}/queue_items', {'track_id': 't1', 'performer_name': 'bob'})
    assert tracks_queued_count() == 1

    response = app.get(f'/comunity/queues?method=delete&format=redirect&queue.id={QUEUE_NEW}')
    # TODO: activate the link above by using the link from soup?
    response = app.get('/comunity/queues')
    assert queue in response.text
    assert QUEUE_NEW not in response.text

    logout(app)

    assert tracks_queued_count() == 0, 'deleting a queue should have cascaded to children. QueueItem residue still present'
