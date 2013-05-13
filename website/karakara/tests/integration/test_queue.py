from karakara.tests.conftest import unimplemented, unfinished, xfail

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

def clear_queue(app):
    for queue_item in get_queue(app):
        del_queue(app, queue_item['id'])
    assert get_queue(app) == []



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
    
    # Check track is in queue list
    response = app.get('/queue')
    assert 'track 1' in response.text
    assert 'testperformer' in response.text
    # Check queue in track description
    response = app.get('/track/t1')
    assert 'testperformer' in response.text
    
    queue_item_id = get_queue(app)[0]['id']
    
    # Remove track from queue
    del_queue(app, queue_item_id)
    
    # Check queue is empty
    assert get_queue(app) == []


def test_queue_errors(app, tracks):
    response = app.post('/queue', dict(track_id='t1000'), expect_errors=True)
    assert response.status_code == 400
    assert 'performer' in response.text  # test should grumble about needing a 'performer' name

    response = app.post('/queue', dict(track_id='t1000', performer_name='test_user'), expect_errors=True)
    assert response.status_code == 400
    assert 'not exist' in response.text

    response = app.put('/queue', {'queue_item.id':'not_real_id'}, expect_errors=True)
    assert response.status_code == 404
    assert 'invalid queue_item.id' in response.text


def test_queue_etag(app, tracks):
    response = app.get('/queue')
    etag = response.etag

    response = app.get('/queue')
    assert etag == response.etag
    
    response = app.post('/queue', dict(track_id='t1', performer_name='testperformer'))
    
    response = app.get('/queue')
    assert etag != response.etag
    
    clear_queue(app)
    

def test_queue_permissions(app, tracks):
    """
    Check only the correct users can remove a queued item
    Check only admin can move items
    """
    assert get_queue(app) == []
    
    # Queue a track
    response = app.post('/queue', dict(track_id='t1', performer_name='testperformer'))
    queue_item_id = get_queue(app)[0]['id']
    # Try to move the track (only admins can move things)
    response = app.put('/queue', {'queue_item.id':queue_item_id, 'queue_item.move.target_id':'any_data'}, expect_errors=True)
    assert response.status_code == 403
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

    # TODO: assert remove button on correct elements on template
    
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
    app.cookiejar.clear() # Loose the cookie so we are not identifyed as the creator of this queue item.
    
    response = del_queue(app, queue_item_id, expect_errors=True)

    # What status's are updated?
    
    
    response = app.get('/admin')
    del_queue(app, queue_item_id)
    response = app.get('/admin')

    assert get_queue(app) == []

def test_queue_played(app, tracks):
    """
    Player system gets track list and removes first queue_item.id when played
    """
    assert get_queue(app) == []
    
    # Add track to queue
    response = app.post('/queue', dict(track_id='t1', performer_name='testperformer'))
    app.cookiejar.clear()
    
    # As admin player mark track as played
    response = app.get('/admin')
    queue_item_id = get_queue(app)[0]['id']
    response = app.put('/queue', {"queue_item.id": queue_item_id, "status": "played", 'format':'json'})
    assert 'update' in response.json['messages'][0]
    response = app.get('/admin')
    
    # TODO: skipped status needs testing too
    
    assert get_queue(app) == []
    #assert DBSession.query # could query actual queue item in db, but that would mean more imports

def test_queue_order(app, tracks):
    """
    Test the queue ordering and weighting system
    Only Admin user should be able to modify the track order
    Admin users should always see the queue in order
    """
    # Test Normal template dose not have form values to move items
    response = app.get('/queue')
    assert 'queue_item.move.target_id' not in response.text, 'Normal users should not be able to move items'
    
    # Ensure queue user is Admin and starting queue state is empty
    response = app.get('/admin')
    assert get_queue(app) == []

    # Test Admin users have form values to move items
    response = app.get('/queue')
    assert 'queue_item.move.target_id' in response.text, 'Admin users should be able to move items'
    
    # Setup queue
    for track_id, performer_name in [
        ('t1','testperformer1'),
        ('t2','testperformer2'),
        ('t3','testperformer3'),
        ('xxx','testperformer4')]:
        response = app.post('/queue', dict(track_id=track_id, performer_name=performer_name))
    queue = get_queue(app)
    assert ['t1','t2','t3','xxx'] == [q['track_id'] for q in queue]
    
    # Move last track to front of queue
    response = app.put('/queue', {'queue_item.id':queue[3]['id'], 'queue_item.move.target_id':queue[0]['id']})
    queue = get_queue(app)
    assert ['xxx','t1','t2','t3'] == [q['track_id'] for q in queue]
    
    # Move second track to back (or as back as we can)
    response = app.put('/queue', {'queue_item.id':queue[1]['id'], 'queue_item.move.target_id':queue[3]['id']})
    queue = get_queue(app)
    assert ['xxx','t2','t1','t3'] == [q['track_id'] for q in queue]
    
    # Tidy queue
    for queue_item in get_queue(app):
        del_queue(app, queue_item['id'])
    assert get_queue(app) == []
    response = app.get('/admin')


def test_queue_template(app,tracks):
    """
    The track order returned by the template should deliberatly obscure
    the order of tracks passed a configurable intavle (eg. 15 min)
    """
    pass


def test_queue_track_duplicate(app, tracks):
    """
    Adding duplicate tracks should error (if appsetting is set)
    """
    assert get_queue(app) == []
    response = app.put('/settings', {'karakara.queue.add.duplicate.count_limit':'1 -> int',
                                     'karakara.queue.add.duplicate.time_limit' :'1:00:00 -> timedelta'})
    response = app.post('/queue', dict(track_id='t1', performer_name='bob1'))
    response = app.post('/queue', dict(track_id='t1', performer_name='bob2'), expect_errors=True)
    assert response.status_code==400
    
    response = app.put('/settings', {'karakara.queue.add.duplicate.count_limit':'0 -> int'})
    clear_queue(app)
    

def test_queue_limit(app, tracks):
    """
    Users should not be able to queue over xx minuets of tracks (settable in config)
    Users trying to add tracks after this time have a 'window period of priority'
    where they have first dibs.
    The user should be informed by the status flash message how long before they
    should retry there selection.
    """
    assert get_queue(app) == []
    response = app.put('/settings', {'karakara.queue.add.limit'       :'0:02:30 -> timedelta',  # 150sec
                                     'karakara.queue.template.padding':'0:00:30 -> timedelta'})

    response = app.post('/queue', dict(track_id='t1', performer_name='bob1')) #total_duration = 0sec
    response = app.post('/queue', dict(track_id='t1', performer_name='bob2')) # 90sec (1min track + 30sec padding)
    response = app.post('/queue', dict(track_id='t1', performer_name='bob3')) #180sec (1min track + 30sec padding) - by adding this track we will be at 180sec, that is now OVER 150sec, the next addition will error
    response = app.post('/queue', dict(track_id='t1', performer_name='bob4'), expect_errors=True)
    assert response.status_code == 400
    
    response = app.put('/settings', {'karakara.queue.add.limit'       :'0:00:00 -> timedelta'})
    clear_queue(app)
