#from karakara.tests.conftest import unimplemented, unfinished, xfail

import datetime
import json
import re
from bs4 import BeautifulSoup

from externals.lib.misc import now

from . import admin_rights


# Utils ------------------------------------------------------------------------

def get_queue(app):
    return app.get('/queue?format=json').json['data']['queue']


def del_queue(app, queue_item_id, expect_errors=False):
    """
    humm .. the current setup is not conforming to the REST standard,
       may need a refactor this
    response = app.delete('/queue', {'queue_item.id':queue_item_id})
    """
    return app.post('/queue', {'method': 'delete', 'queue_item.id': queue_item_id}, expect_errors=expect_errors)


def clear_queue(app):
    for queue_item in get_queue(app):
        del_queue(app, queue_item['id'])
    assert get_queue(app) == []


def get_cookie(app, key):
    try:
        return json.loads({cookie.name: cookie for cookie in app.cookiejar}[key].value)
    except KeyError:
        return None


def add_queue(app, track_id, performer_name):
    response = app.post('/queue', dict(track_id=track_id, performer_name=performer_name))
    assert response.status_code == 201


def admin_play_next_track(app):
    """
    As admin player mark track as played
    """
    response = app.get('/admin')
    queue_item_id = get_queue(app)[0]['id']
    response = app.put('/queue', {"queue_item.id": queue_item_id, "status": "played", 'format': 'json'})
    assert 'update' in response.json['messages'][0]
    response = app.get('/admin')


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
    assert 'track 1' not in response.text.lower()

    # Queue 'Track 1'
    response = app.post('/queue', dict(track_id='t1', performer_name='testperformer'))

    # Check track is in queue list
    response = app.get('/queue')
    assert 'track 1' in response.text.lower()
    assert 'testperformer' in response.text.lower()
    # Check queue in track description
    response = app.get('/track/t1')
    assert 'testperformer' in response.text.lower()

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

    response = app.put('/queue', {'queue_item.id': 'not_real_id'}, expect_errors=True)
    assert response.status_code == 404
    assert 'invalid queue_item.id' in response.text


def test_queue_etag(app, tracks):
    # First response has etag
    response = app.get('/queue')
    etag_queue = response.etag
    response = app.get('/track/t1')
    etag_track = response.etag

    # Second request to same resource has same etag
    response = app.get('/queue')
    assert etag_queue == response.etag
    response = app.get('/track/t1')
    assert etag_track == response.etag

    # Change the queue - this should invalidate the etag
    response = app.post('/queue', dict(track_id='t1', performer_name='testperformer'))

    # Assert etag has changed
    response = app.get('/queue')
    assert etag_queue != response.etag
    etag_queue = response.etag
    response = app.get('/track/t1')
    assert etag_track != response.etag
    etag_track = response.etag

    response = app.get('/queue', headers={'If-None-Match': etag_queue})
    assert response.status_code == 304
    response = app.get('/track/t1', headers={'If-None-Match': etag_track})
    assert response.status_code == 304

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
    response = app.put('/queue', {'queue_item.id': queue_item_id, 'queue_item.move.target_id': 9999}, expect_errors=True)
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


def test_queue_played(app, tracks):
    """
    Player system gets track list and removes first queue_item.id when played
    """
    assert get_queue(app) == []

    # Add track to queue
    app.post('/queue', dict(track_id='t1', performer_name='testperformer'))

    # Try to set as 'played' as normal user - and get rejected
    app.cookiejar.clear()  # Loose the cookie so we are not identifyed as the creator of this queue item.
    queue_item_id = get_queue(app)[0]['id']
    app.put('/queue', {"queue_item.id": queue_item_id, "status": "played", 'format': 'json'}, expect_errors=True)

    # As admin player mark track as played
    admin_play_next_track(app)

    # TODO: skipped status needs testing too

    assert get_queue(app) == []
    #assert DBSession.query # could query actual queue item in db, but that would mean more imports


def test_queue_reorder(app, tracks):
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
        ('t1', 'testperformer1'),
        ('t2', 'testperformer2'),
        ('t3', 'testperformer3'),
        ('xxx', 'testperformer4')
    ]:
        add_queue(app, track_id, performer_name)
    queue = get_queue(app)
    assert ['t1', 't2', 't3', 'xxx'] == [q['track_id'] for q in queue]

    # Move last track to front of queue
    response = app.put('/queue', {'queue_item.id': queue[3]['id'], 'queue_item.move.target_id': queue[0]['id']})
    queue = get_queue(app)
    assert ['xxx', 't1', 't2', 't3'] == [q['track_id'] for q in queue]

    # Move second track to infont of last item
    response = app.put('/queue', {'queue_item.id': queue[1]['id'], 'queue_item.move.target_id': queue[-1]['id']})
    queue = get_queue(app)
    assert ['xxx', 't2', 't1', 't3'] == [q['track_id'] for q in queue]

    # Check moving to a destination id that does not exisit yeilds the end of the queue
    response = app.put('/queue', {'queue_item.id': queue[1]['id'], 'queue_item.move.target_id': 65535})
    queue = get_queue(app)
    assert ['xxx', 't1', 't3', 't2'] == [q['track_id'] for q in queue]

    # Check normal users cannot change order
    response = app.get('/admin')  # turn off admin
    response = app.put('/queue', {'queue_item.id': queue[1]['id'], 'queue_item.move.target_id': queue[3]['id']}, expect_errors=True)
    assert response.status_code == 403
    assert 'admin only' in response.text
    queue = get_queue(app)
    assert ['xxx', 't1', 't3', 't2'] == [q['track_id'] for q in queue]

    # Tidy queue
    clear_queue(app)


def test_queue_obscure(app, tracks):
    """
    The track order returned by the template should deliberatly obscured
    the order of tracks passed a configurable intavle (eg. 15 min)

    This is acomplished by calculating a split_index
    clients of the api are expected to obscure the order where nessisary
    """
    assert get_queue(app) == []

    app.put('/settings.json', {'karakara.queue.group.split_markers': '[0:02:00, 0:10:00] -> timedelta'})
    assert app.put('/settings.json').json['data']['settings']['karakara.queue.group.split_markers'][0] == 120.0, 'Settings not updated'

    # Test API and Logic

    for track_id, performer_name in [
        ('t1', 'testperformer1'),  #  60sec + 30sec padding = 1:00 + 0:30        = 1:30
        ('t2', 'testperformer2'),  # 120sec + padding       = 1:30 + 2:00 + 0:30 = 4:00 
        ('t3', 'testperformer3'),  # 240sec + padding       = 4:00 + 4:00 + 0:30 = 8:30
    ]:
        add_queue(app, track_id, performer_name)

    data = app.get('/queue?format=json').json['data']
    assert len(data['queue_split_indexs']) == 1
    assert data['queue_split_indexs'][0] == 2

    # Test Template Display
    soup = BeautifulSoup(app.get('/queue').text)
    def get_track_ids(_class):
        return [re.match(r'.*/(.*)', li.a['href']).group(1) for li in soup.find(**{'class': _class}).find_all('li')]
    queue_list = get_track_ids('queue-list')
    assert 't1' == queue_list[0]
    assert 't2' == queue_list[1]
    assert len(queue_list) == 2
    queue_grid = get_track_ids('queue-grid')
    assert 't3' in queue_grid
    assert len(queue_grid) == 1

    clear_queue(app)


def test_queue_track_duplicate(app, tracks, DBSession, commit):
    """
    Adding duplicate tracks should error (if appsetting is set)
    """
    assert get_queue(app) == []
    response = app.put('/settings', {'karakara.queue.add.duplicate.track_limit': '1 -> int',
                                     'karakara.queue.add.duplicate.time_limit': '1:00:00 -> timedelta'})

    # Duplicate also looks at 'played' tracks
    # These are not surfaced by the queue API so we need to DB access to clean out the leftover played references
    from karakara.model.model_queue import QueueItem
    for queue_item in DBSession.query(QueueItem).filter(QueueItem.track_id == 't1').filter(QueueItem.status == 'played').all():
        DBSession.delete(queue_item)
    commit()

    response = app.post('/queue', dict(track_id='t1', performer_name='bob1'))
    response = app.post('/queue', dict(track_id='t1', performer_name='bob2'), expect_errors=True)
    assert response.status_code == 400

    response = app.put('/settings', {'karakara.queue.add.duplicate.track_limit': '0 -> int'})
    clear_queue(app)


def test_queue_performer_duplicate(app, tracks, DBSession, commit):
    assert get_queue(app) == []
    response = app.put('/settings', {
        'karakara.queue.add.duplicate.performer_limit': '1 -> int',
    })

    def clear_played():
        # Duplicate also looks at 'played' tracks
        # These are not surfaced by the queue API so we need to DB access to clean out the leftover played references
        from karakara.model.model_queue import QueueItem
        for queue_item in DBSession.query(QueueItem).filter(QueueItem.performer_name == 'bob').filter(QueueItem.status == 'played').all():
            DBSession.delete(queue_item)
        commit()
    clear_played()

    response = app.post('/queue', dict(track_id='t1', performer_name='bob'))
    response = app.post('/queue', dict(track_id='t1', performer_name='bob'), expect_errors=True)
    assert response.status_code == 400
    assert 'bob' in BeautifulSoup(response.text).find(**{'class': 'flash_message'}).text.lower()

    response = app.put('/settings', {
        'karakara.queue.add.duplicate.performer_limit': '0 -> int',
    })
    clear_queue(app)
    clear_played()

    response = app.post('/queue', dict(track_id='t1', performer_name='bob'))
    response = app.post('/queue', dict(track_id='t1', performer_name='bob'))

    clear_queue(app)
    clear_played()


def test_queue_limit(app, tracks):
    """
    Users should not be able to queue over xx minuets of tracks (settable in config)
    Users trying to add tracks after this time have a 'window period of priority'
    where they have first dibs.
    The user should be informed by the status flash message how long before they
    should retry there selection.
    """
    assert get_queue(app) == []
    response = app.put('/settings', {
        'karakara.queue.add.limit'                : '0:02:30 -> timedelta',  # 150sec
        'karakara.queue.track.padding'            : '0:00:30 -> timedelta',
        'karakara.queue.add.limit.priority_window': '0:05:00 -> timedelta',
    })

    # Ensure we don't have an existing priority token
    assert not get_cookie(app, 'priority_token')

    # Fill the Queue
    response = app.post('/queue', dict(track_id='t1', performer_name='bob1'))  # total_duration = 0sec
    response = app.post('/queue', dict(track_id='t1', performer_name='bob2'))  #  90sec (1min track + 30sec padding)
    response = app.post('/queue', dict(track_id='t1', performer_name='bob3'))  # 180sec (1min track + 30sec padding) - by adding this track we will be at 180sec, that is now OVER 150sec, the next addition will error

    # Fail quque add, get priority token
    response = app.post('/queue', dict(track_id='t1', performer_name='bob4'), expect_errors=True)
    assert response.status_code == 400
    cookie_priority_token = get_cookie(app, 'priority_token')
    assert cookie_priority_token.get('valid_start')
    assert cookie_priority_token.get('server_datetime')

    # Try queue add again and not get priority token give as we already have one
    response = app.post('/queue.json', dict(track_id='t1', performer_name='bob4'), expect_errors=True)
    assert 'already have' in response.json['messages'][0]

    # Shift server time forward - simulate waiting 5 minuets - we should be in our priority token range
    now(now() + datetime.timedelta(minutes=5))

    # Add the track using the power of the priority token
    response = app.post('/queue', dict(track_id='t1', performer_name='bob4'))
    assert 'bob4' in [q['performer_name'] for q in get_queue(app)]
    assert not get_cookie(app, 'priority_token')  # The priority token should be consumed and removed from the client

    # Tidyup after test
    now(datetime.datetime.now())
    response = app.put('/settings', {
        'karakara.queue.add.limit': '0:00:00 -> timedelta'
    })
    clear_queue(app)


def test_event_end(app, tracks):
    assert get_queue(app) == []

    response = app.put('/settings', {
        'karakara.event.end': '{0} -> datetime'.format(now()+datetime.timedelta(minutes=0, seconds=30)),
    })

    response = app.post('/queue', dict(track_id='t1', performer_name='bob'))
    response = app.post('/queue', dict(track_id='t1', performer_name='bob'), expect_errors=True)
    assert response.status_code == 400
    assert 'ending soon' in response.text

    response = app.put('/settings', {
        'karakara.event.end': ' -> datetime',
    })
    clear_queue(app)


@admin_rights
def test_priority_tokens(app):
    response = app.get('/priority_tokens')
    assert response.status_code == 200
