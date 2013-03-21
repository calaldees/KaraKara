


def test_queue_view_simple_add_delete_cycle(app, tracks):
    """
    View empty queue
    queue a track
    remove a track
    """
    def get_queue():
        return app.get('/queue?format=json').json['data']['queue']
    
    response = app.get('/queue')
    assert 'track 1' not in response.text    
    assert get_queue() == []
    
    response = app.post('/queue', dict(track_id='t1', performer_name='testperformer'))
    
    response = app.get('/queue')
    assert 'track 1' in response.text
    assert 'testperformer' in response.text
    queue_item_id = get_queue()[0]['id']
    
    #response = app.delete('/queue', {'queue_item.id':queue_item_id})
    response = app.post('/queue', {'method':'delete', 'queue_item.id':queue_item_id})
    assert get_queue() == []
