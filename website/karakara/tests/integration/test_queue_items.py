import pytest

import datetime
import json
import re
import bs4
def BeautifulSoup(markup):
    return bs4.BeautifulSoup(markup, "html.parser")

from externals.lib.misc import now

from . import admin_rights, with_settings, temporary_settings


# Utils ------------------------------------------------------------------------

class QueueManager():

    def __init__(self, app, queue):
        self.app = app
        self.queue = queue
        self.queue_items_url = f'/queue/{queue}/queue_items'
        self.queue_settings_url = f'/queue/{queue}/settings'

    @property
    def settings(self):
        return self.app.get(f'{self.queue_settings_url}?format=json').json['data']['settings']

    def get_html_response(self):
        return self.app.get(self.queue_items_url)

    @property
    def soup(self):
        return BeautifulSoup(self.get_html_response().text)

    @property
    def data(self):
        return self.app.get(f'{self.queue_items_url}?format=json').json['data']

    @property
    def items(self):
        return self.data['queue']

    def add_queue_item(self, track_id, performer_name, expect_errors=False):
        response = self.app.post(self.queue_items_url, dict(track_id=track_id, performer_name=performer_name), expect_errors=expect_errors)
        if not expect_errors:
            assert response.status_code == 201
        return response

    def del_queue_item(self, queue_item_id, expect_errors=False):
        """
        humm .. the current setup is not conforming to the REST standard,
        may need a refactor this
        response = app.delete('/queue', {'queue_item.id':queue_item_id})
        """
        return self.app.post(self.queue_items_url, {'method': 'delete', 'queue_item.id': queue_item_id}, expect_errors=expect_errors)

    def move_queue_item(self, queue_index, queue_index_target, expect_errors=False):
        queue_ids = [q['id'] for q in self.items]
        return self.app.put(
            self.queue_items_url,
            {
                'queue_item.id': queue_ids[queue_index],
                'queue_item.move.target_id': queue_ids[queue_index_target],
            },
            expect_errors=expect_errors,
        )

    def clear(self):
        for queue_item in self.items:
            self.del_queue_item(queue_item['id'])
        assert self.items == []

    def admin_play_next_track(self):
        """
        As admin player mark track as played
        """
        queue_length = len(self.items)
        with admin_rights(self.app, self.queue):
            queue_item_id = self.items[0]['id']
            response = self.app.put(self.queue_items_url, {"queue_item.id": queue_item_id, "status": "played", 'format': 'json'})
            assert 'update' in response.json['messages'][0]
        assert queue_length - 1 == len(self.items)


@pytest.yield_fixture(scope='function')
def queue_manager(app, queue):
    queue_manager = QueueManager(app, queue)
    assert len(queue_manager.items) == 0
    yield queue_manager
    queue_manager.clear()


def get_cookie(app, key):
    try:
        return json.loads({cookie.name: cookie for cookie in app.cookiejar}[key].value)
    except KeyError:
        return None


# Tests ------------------------------------------------------------------------

def test_queue_view_simple_add_delete_cycle(app, queue, queue_manager, tracks):
    """
    View empty queue
    queue a track
    remove a track
    """

    # Check no tracks in queue
    response = queue_manager.get_html_response()
    assert 'track 1' not in response.text.lower()

    # Queue 'Track 1'
    queue_manager.add_queue_item(track_id='t1', performer_name='testperformer')

    # Check track is in queue list
    response = queue_manager.get_html_response()
    assert 'track 1' in response.text.lower()
    assert 'testperformer' in response.text.lower()
    # Check queue in track description
    response = app.get(f'/queue/{queue}/track/t1')
    assert 'testperformer' in response.text.lower()


def test_queue_errors(app, queue, queue_manager, tracks):
    queue_items_url = queue_manager.queue_items_url

    response = app.post(queue_items_url, dict(track_id='t1000'), expect_errors=True)
    assert response.status_code == 400
    assert 'performer' in response.text  # test should grumble about needing a 'performer' name

    response = app.post(queue_items_url, dict(track_id='t1000', performer_name='test_user'), expect_errors=True)
    assert response.status_code == 400
    assert 'not exist' in response.text

    response = app.put(queue_items_url, {'queue_item.id': 'not_real_id'}, expect_errors=True)
    assert response.status_code == 404
    assert 'invalid queue_item.id' in response.text


def test_queue_etag(app, queue, queue_manager, tracks):
    queue_items_url = queue_manager.queue_items_url
    track_url = f'/queue/{queue}/track/t1'

    # First response has etag
    response = queue_manager.get_html_response()
    etag_queue = response.etag
    response = app.get(track_url)
    etag_track = response.etag

    # Second request to same resource has same etag
    response = queue_manager.get_html_response()
    assert etag_queue == response.etag
    response = app.get(track_url)
    assert etag_track == response.etag

    # Change the queue - this should invalidate the etag
    response = queue_manager.add_queue_item(track_id='t1', performer_name='testperformer')

    # Assert etag has changed
    response = queue_manager.get_html_response()
    assert etag_queue != response.etag
    etag_queue = response.etag
    response = app.get(track_url)
    assert etag_track != response.etag
    etag_track = response.etag

    response = app.get(queue_items_url, headers={'If-None-Match': etag_queue})
    assert response.status_code == 304
    response = app.get(track_url, headers={'If-None-Match': etag_track})
    assert response.status_code == 304


def test_queue_permissions(app, queue, queue_manager, tracks):
    """
    Check only the correct users can remove a queued item
    Check only admin can move items
    """
    # Queue a track
    queue_manager.add_queue_item(track_id='t1', performer_name='testperformer')
    #response = app.post('/queue', dict(track_id='t1', performer_name='testperformer'))
    queue_item_id = queue_manager.items[0]['id']
    # Try to move the track (only admins can move things)
    response = app.put(queue_manager.queue_items_url, {'queue_item.id': queue_item_id, 'queue_item.move.target_id': 9999}, expect_errors=True)
    assert response.status_code == 403
    # Clear the cookies (ensure we are a new user)
    app.cookiejar.clear()
    # Attempt to delete the queued track (should fail)
    response = queue_manager.del_queue_item(queue_item_id, expect_errors=True)
    assert response.status_code == 403
    assert len(queue_manager.items) == 1, 'the previous user should not of had permissions to remove the item from the queue'
    # Become an admin, del track, remove admin status
    with admin_rights(app, queue):
        queue_manager.del_queue_item(queue_item_id)

    # TODO: assert remove button on correct elements on template


def test_queue_played(app, queue, queue_manager, tracks):
    """
    Player system gets track list and removes first queue_item.id when played
    """
    # Add track to queue
    queue_manager.add_queue_item(track_id='t1', performer_name='testperformer')
    assert len(queue_manager.items) == 1

    # Try to set as 'played' as normal user - and get rejected
    app.cookiejar.clear()  # Loose the cookie so we are not identifyed as the creator of this queue item.
    queue_item_id = queue_manager.items[0]['id']
    app.put(queue_manager.queue_items_url, {"queue_item.id": queue_item_id, "status": "played", 'format': 'json'}, expect_errors=True)
    assert len(queue_manager.items) == 1

    # As admin player mark track as played
    queue_manager.admin_play_next_track()

    # TODO: 'skipped status' needs testing too - maybe query actual db?

    assert len(queue_manager.items) == 0


def test_queue_reorder(app, queue, queue_manager, tracks):
    """
    Test the queue ordering and weighting system
    Only Admin user should be able to modify the track order
    Admin users should always see the queue in order
    """
    def get_track_ids():
        return [q['track_id'] for q in queue_manager.items]
    def get_queue_ids():
        return [q['id'] for q in queue_manager.items]

    # Test Normal template dose not have form values to move items
    response = queue_manager.get_html_response()
    assert 'queue_item.move.target_id' not in response.text, 'Normal users should not be able to move items'

    # Ensure queue user is Admin and starting queue state is empty
    with admin_rights(app, queue):
        assert not queue_manager.items

        # Test Admin users have form values to move items
        response = queue_manager.get_html_response()
        assert 'queue_item.move.target_id' in response.text, 'Admin users should be able to move items'

        # Setup queue
        for track_id, performer_name in [
            ('t1', 'testperformer1'),
            ('t2', 'testperformer2'),
            ('t3', 'testperformer3'),
            ('xxx', 'testperformer4')
        ]:
            queue_manager.add_queue_item(track_id, performer_name)
        assert ['t1', 't2', 't3', 'xxx'] == get_track_ids()

        # Move last track to front of queue
        queue_manager.move_queue_item(3, 0)
        assert ['xxx', 't1', 't2', 't3'] == get_track_ids()

        # Move second track to infont of last item
        queue_manager.move_queue_item(1, -1)
        assert ['xxx', 't2', 't1', 't3'] == get_track_ids()

        # Check moving to a destination id that does not exisit yeilds the end of the queue
        response = app.put(
            queue_manager.queue_items_url,
            {
                'queue_item.id': queue_manager.items[1]['id'],
                'queue_item.move.target_id': 65535,
            },
        )
        assert ['xxx', 't1', 't3', 't2'] == get_track_ids()

    # Check normal users cannot change order
    response = queue_manager.move_queue_item(1, 3, expect_errors=True)
    assert response.status_code == 403
    assert 'admin only' in response.text

    assert ['xxx', 't1', 't3', 't2'] == get_track_ids()


@with_settings(settings={
    'karakara.queue.group.split_markers': '[0:02:00, 0:10:00]',  # -> timedelta
})
def test_queue_obscure(app, queue, queue_manager, tracks):
    """
    The track order returned by the template should deliberately obscured
    the order of tracks passed a configurable intaval (eg. 15 min)

    This is accomplished by calculating a split_index
    clients of the api are expected to obscure the order where necessarily
    """
    assert queue_manager.settings['karakara.queue.group.split_markers'][0] == 120.0, 'Settings not updated'

    # Test API and Logic
    for track_id, performer_name in [
        ('t1', 'testperformer1'),  #  60sec + 30sec padding = 1:00 + 0:30        = 1:30
        ('t2', 'testperformer2'),  # 120sec + padding       = 1:30 + 2:00 + 0:30 = 4:00
        ('t3', 'testperformer3'),  # 240sec + padding       = 4:00 + 4:00 + 0:30 = 8:30
    ]:
        queue_manager.add_queue_item(track_id, performer_name)

    data = queue_manager.data
    assert len(data['queue_split_indexs']) == 1
    assert data['queue_split_indexs'][0] == 2

    # Test Template Display
    soup = queue_manager.soup
    def get_track_ids(_class):
        return [re.match(r'.*/(.*)', li.a['href']).group(1) for li in soup.find(**{'class': _class}).find_all('li')]
    queue_list = get_track_ids('queue-list')
    assert 't1' == queue_list[0]
    assert 't2' == queue_list[1]
    assert len(queue_list) == 2
    queue_grid = get_track_ids('queue-grid')
    assert 't3' in queue_grid
    assert len(queue_grid) == 1


@with_settings(settings={
    'karakara.queue.add.duplicate.track_limit': 1,
    'karakara.queue.add.duplicate.time_limit': '1:00:00',  # -> timedelta
})
def test_queue_track_duplicate(app, queue, tracks, queue_manager, DBSession, commit):
    """
    Adding duplicate tracks should error (if appsetting is set)
    """
    # Duplicate also looks at 'played' tracks
    # These are not surfaced by the queue API so we need to DB access to clean out the leftover played references
    from karakara.model.model_queue import QueueItem
    for queue_item in DBSession.query(QueueItem).filter(QueueItem.track_id == 't1').filter(QueueItem.status == 'played').all():
        DBSession.delete(queue_item)
    commit()

    response = queue_manager.add_queue_item(track_id='t1', performer_name='bob1')
    response = queue_manager.add_queue_item(track_id='t1', performer_name='bob2', expect_errors=True)
    assert response.status_code == 400


def test_queue_performer_duplicate(app, queue, queue_manager, tracks, DBSession, commit):

    def clear_played():
        # Duplicate also looks at 'played' tracks
        # These are not surfaced by the queue API so we need to DB access to clean out the leftover played references
        from karakara.model.model_queue import QueueItem
        for queue_item in DBSession.query(QueueItem).filter(QueueItem.performer_name == 'bob').filter(QueueItem.status == 'played').all():
            DBSession.delete(queue_item)
        commit()
    clear_played()


    with temporary_settings(app, queue, {'karakara.queue.add.duplicate.performer_limit': 1}):
        response = queue_manager.add_queue_item(track_id='t1', performer_name='bob')
        response = queue_manager.add_queue_item(track_id='t1', performer_name='bob', expect_errors=True)
        assert response.status_code == 400
        assert 'bob' in BeautifulSoup(response.text).find(**{'class': 'flash_message'}).text.lower()

    #response = app.put('/settings', {'karakara.queue.add.duplicate.performer_limit': '0 -> int',})
    clear_played()
    queue_manager.clear()

    with temporary_settings(app, queue, {'karakara.queue.add.duplicate.performer_limit': 0}):
        response = queue_manager.add_queue_item(track_id='t1', performer_name='bob')
        response = queue_manager.add_queue_item(track_id='t1', performer_name='bob')

    clear_played()


@with_settings(settings={
    'karakara.queue.add.valid_performer_names': '[bob, jim, sally]',
})
def test_queue_performer_restrict(app, queue, queue_manager, tracks, DBSession, commit):
    response = queue_manager.add_queue_item(track_id='t1', performer_name='bob')
    response = queue_manager.add_queue_item(track_id='t1', performer_name='Bob')  # Valid performer names should be case insensetive
    response = queue_manager.add_queue_item(track_id='t1', performer_name='jane', expect_errors=True)
    assert response.status_code == 400
    assert 'jane' in BeautifulSoup(response.text).find(**{'class': 'flash_message'}).text.lower()


@with_settings(settings={
    'karakara.queue.add.limit'                : '0:02:30',  # 150sec
    'karakara.queue.track.padding'            : '0:00:30',
    'karakara.queue.add.limit.priority_window': '0:05:00',
})
def test_queue_limit(app, queue, queue_manager, tracks):
    """
    Users should not be able to queue over xx minuets of tracks (settable in config)
    Users trying to add tracks after this time have a 'window period of priority'
    where they have first dibs.
    The user should be informed by the status flash message how long before they
    should retry there selection.
    """
    # Ensure we don't have an existing priority token
    assert not get_cookie(app, 'priority_token')

    # Fill the Queue
    response = queue_manager.add_queue_item(track_id='t1', performer_name='bob1')  # total_duration = 0sec
    response = queue_manager.add_queue_item(track_id='t1', performer_name='bob2')  #  90sec (1min track + 30sec padding)
    response = queue_manager.add_queue_item(track_id='t1', performer_name='bob3')  # 180sec (1min track + 30sec padding) - by adding this track we will be at 180sec, that is now OVER 150sec, the next addition will error

    # Fail quque add, get priority token
    response = queue_manager.add_queue_item(track_id='t1', performer_name='bob4', expect_errors=True)
    assert response.status_code == 400
    cookie_priority_token = get_cookie(app, 'priority_token')
    assert cookie_priority_token.get('valid_start')
    assert cookie_priority_token.get('server_datetime')

    # Try queue add again and not get priority token give as we already have one
    response = queue_manager.add_queue_item(track_id='t1', performer_name='bob4', expect_errors=True)
    #assert 'already have' in response.json['messages'][0]
    assert 'already have' in response.text

    # Shift server time forward - simulate waiting 5 minuets - we should be in our priority token range
    now(now() + datetime.timedelta(minutes=5))

    # Add the track using the power of the priority token
    response = queue_manager.add_queue_item(track_id='t1', performer_name='bob4')
    assert 'bob4' in [q['performer_name'] for q in queue_manager.items]
    assert not get_cookie(app, 'priority_token')  # The priority token should be consumed and removed from the client

    # Tidyup after test
    now(datetime.datetime.now())


@with_settings(settings={
    'karakara.event.end': str(now() + datetime.timedelta(minutes=0, seconds=30)),
})
def test_event_end(app, queue, queue_manager, tracks):
    response = queue_manager.add_queue_item(track_id='t1', performer_name='bob')
    response = queue_manager.add_queue_item(track_id='t1', performer_name='bob', expect_errors=True)
    assert response.status_code == 400
    assert 'ending soon' in response.text


def test_priority_tokens(app, queue):
    with admin_rights(app, queue):
        response = app.get('/priority_tokens')
        assert response.status_code == 200
