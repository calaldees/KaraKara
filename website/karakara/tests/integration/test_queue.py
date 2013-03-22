from karakara.tests.conftest import unimplemented, unfinished

# Utils ------------------------------------------------------------------------

def get_queue(app):
    return app.get('/queue?format=json').json['data']['queue']

def del_queue(app, queue_item_id, expect_errors=False):
    """
    humm .. the current setup is not conforming to the REST standard,
       may need a refactor this
    response = app.delete('/queue', {'queue_item.id':queue_item_id})
    """
    return app.post('/queue', {'method':'delete', 'queue_item.id':queue_item_id}, expect_errors=expect_errors)


# Tests ------------------------------------------------------------------------

def test_queue_view_simple_add_delete_cycle(app, tracks):
    """
    View empty queue
    queue a track
    remove a track
    """
    assert get_queue(app) == []
    
    # Check no tracks in queue
    response = app.get('/queue')
    assert 'track 1' not in response.text
    
    # Queue 'Track 1'
    response = app.post('/queue', dict(track_id='t1', performer_name='testperformer'))
    
    # Check track is in queue
    response = app.get('/queue')
    assert 'track 1' in response.text
    assert 'testperformer' in response.text
    queue_item_id = get_queue(app)[0]['id']
    
    # Remove track from queue
    del_queue(app, queue_item_id)
    
    # Check queue is empty
    assert get_queue(app) == []


@unimplemented
def test_queue_view_add_del_permissions(app, tracks):
    """
    Check only the correct users can remove a queued item 
    """
    assert get_queue(app) == []
    
    # Queue a track
    response = app.post('/queue', dict(track_id='t1', performer_name='testperformer'))
    queue_item_id = get_queue(app)[0]['id']
    # Clear the cookies (ensure we are a new user)
    app.cookiejar.clear()
    # Attempt to delete the queued track (should fail)
    response = del_queue(app, queue_item_id, expect_errors=True)
    assert response.status_code == 403
    assert len(get_queue(app)) == 1, 'the previous user should not of had permissions to remove the item from the queue'
    # Become an admin, del track, remove admin status
    response = app.get('/admin')
    del_queue(app, queue_item_id)
    response = app.get('/admin')
    
    assert get_queue(app) == []

@unfinished
def test_queue_view_update(app, tracks):
    """
    Update track status
    played
    performer?
    order?
    """
    assert get_queue(app) == []
    response = app.post('/queue', dict(track_id='t1', performer_name='testperformer'))
    app.cookiejar.clear()
    
    response = app.put('/queue', {'queue_item.id':'not_real_id'}, expect_errors=True)
    assert response.status_code == 400
    assert 'invalid queue_item.id' in response.text

    response = del_queue(app, queue_item_id, expect_errors=True)

    # What status's are updated?
    
    
    response = app.get('/admin')
    del_queue(app, queue_item_id)
    response = app.get('/admin')

    assert get_queue(app) == []