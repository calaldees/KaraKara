
# Utils ------------------------------------------------------------------------

def get_queue(app):
    return app.get('/queue?format=json').json['data']['queue']

def del_queue(app, queue_item_id):
    """
    humm .. the current setup is not conforming to the REST standard,
       may need a refactor this
    response = app.delete('/queue', {'queue_item.id':queue_item_id})
    """
    return app.post('/queue', {'method':'delete', 'queue_item.id':queue_item_id})


# Tests ------------------------------------------------------------------------

def test_queue_view_simple_add_delete_cycle(app, tracks):
    """
    View empty queue
    queue a track
    remove a track
    """
    
    response = app.get('/queue')
    assert 'track 1' not in response.text    
    assert get_queue(app) == []
    
    response = app.post('/queue', dict(track_id='t1', performer_name='testperformer'))
    
    response = app.get('/queue')
    assert 'track 1' in response.text
    assert 'testperformer' in response.text
    queue_item_id = get_queue(app)[0]['id']
    
    del_queue(app, queue_item_id)
    assert get_queue(app) == []


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
    del_queue(app, queue_item_id)
    assert len(get_queue(app)) == 1, 'the previous user should not of had permissions to remove the item from the queue'
