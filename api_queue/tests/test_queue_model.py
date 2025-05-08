import pytest

import datetime

from api_queue.queue_model import Queue, QueueItem

from api_queue.settings_manager import QueueSettings

ONE_MINUTE = datetime.timedelta(seconds=60)

@pytest.fixture
def qu() -> Queue:
    qu = Queue([], settings=QueueSettings(track_space=datetime.timedelta(seconds=10)))
    qu._now = datetime.datetime(2022, 1, 1, tzinfo=datetime.timezone.utc)
    return qu

def test_queue_empty(qu: Queue):
    assert not qu.current
    assert not qu.playing

def test_queue_add_tracks(qu: Queue):
    qu.add(QueueItem('Track1', ONE_MINUTE, 'TestSession1', 'test_name'))
    assert [i.track_id for i in qu.items] == ['Track1']
    assert qu.current
    assert qu.current.track_id == 'Track1'
    assert not qu.current.start_time
    qu.add(QueueItem('Track2', ONE_MINUTE, 'TestSession2', 'test_name'))
    assert [i.track_id for i in qu.items] == ['Track1', 'Track2']
    assert qu.current.track_id == 'Track1'

def test_queue_time_moves_forwards(qu: Queue):
    assert qu._now
    qu.add(QueueItem('Track1', ONE_MINUTE, 'TestSession1', 'test_name'))
    qu.add(QueueItem('Track2', ONE_MINUTE, 'TestSession2', 'test_name'))

    # Playing state when moving time forward
    qu.play()  # play queues a track to start in 1s
    assert qu.playing is None
    qu._now += datetime.timedelta(seconds=1)
    assert qu.playing
    assert qu.playing.track_id == 'Track1'
    qu._now += datetime.timedelta(seconds=30)
    assert qu.playing.track_id == 'Track1'
    qu._now += datetime.timedelta(seconds=30)
    assert not qu.playing
    qu._now += datetime.timedelta(seconds=30)
    assert qu.playing.track_id == 'Track2'
    qu._now += datetime.timedelta(seconds=30)
    assert qu.playing.track_id == 'Track2'
    qu._now += datetime.timedelta(seconds=30)
    assert not qu.playing

def test_queue_past_future(qu: Queue):
    assert qu._now
    qu.add(QueueItem('Track1', ONE_MINUTE, 'TestSession1', 'test_name'))
    qu.add(QueueItem('Track2', ONE_MINUTE, 'TestSession2', 'test_name'))
    qu.play(immediate=True)
    qu._now += datetime.timedelta(seconds=150)

    # Past tracks
    assert [i.track_id for i in qu.items] == ['Track1', 'Track2']
    assert [i.track_id for i in qu.past] == ['Track1', 'Track2']
    assert [i.track_id for i in qu.future] == []

    # Can't delete past items
    assert [i.track_id for i in qu.past] == ['Track1', 'Track2']
    past_track_id = [i for i in qu.past][1].id
    qu.delete(past_track_id)
    assert [i.track_id for i in qu.past] == ['Track1', 'Track2']

def test_queue_append(qu: Queue):
    assert qu._now
    qu.add(QueueItem('Track1', ONE_MINUTE, 'TestSession1', 'test_name'))
    qu.add(QueueItem('Track2', ONE_MINUTE, 'TestSession2', 'test_name'))
    qu.play(immediate=True)
    qu._now += datetime.timedelta(seconds=150)
    # Adding + Deleting + Future + current tracks work after played past tracks
    qu.add(QueueItem('Track3', ONE_MINUTE, 'TestSession3', 'test_name'))
    qu.add(QueueItem('Track4', ONE_MINUTE, 'TestSession4', 'test_name'))
    assert not qu.playing
    assert qu.current
    assert qu.current.track_id == 'Track3'
    assert [i.track_id for i in qu.future] == ['Track3', 'Track4']
    qu.delete(qu.current.id)
    assert [i.track_id for i in qu.future] == ['Track4']
    assert qu.current
    assert qu.current.track_id == 'Track4'

def test_queue_delete_playing_item_stops_playback(qu: Queue):
    assert qu._now
    qu.add(QueueItem('Track1', ONE_MINUTE, 'TestSession1', 'test_name'))
    qu.add(QueueItem('Track2', ONE_MINUTE, 'TestSession2', 'test_name'))
    qu.add(QueueItem('Track3', ONE_MINUTE, 'TestSession2', 'test_name'))
    qu.play(immediate=True)
    assert qu.playing
    assert qu.last
    qu.delete(qu.last.id)
    assert qu.playing, 'deleting future items should not stop playback'
    qu.delete(qu.playing.id)
    assert not qu.playing, 'deleting the current playing item should stop playback'
    assert qu.current and qu.current.track_id == 'Track2'

def test_queue_delete_scheduled_playing_item_stops_playback(qu: Queue):
    assert qu._now
    qu.add(QueueItem('Track1', ONE_MINUTE, 'TestSession1', 'test_name'))
    qu.add(QueueItem('Track2', ONE_MINUTE, 'TestSession2', 'test_name'))
    qu.add(QueueItem('Track3', ONE_MINUTE, 'TestSession2', 'test_name'))
    qu.play(immediate=False)  # queue to start playing in 1 second time
    assert not qu.playing
    assert qu.items[0].start_time, 'all items should have start_time'
    assert qu.items[1].start_time, 'all items should have start_time'
    qu.delete(qu.items[0].id)
    assert qu.current and not qu.current.start_time, 'playback should have stopped'

def test_queue_append_while_playing_populates_start_time(qu: Queue):
    assert qu._now
    qu.add(QueueItem('Track4', ONE_MINUTE, 'TestSession4', 'test_name'))
    qu._now += datetime.timedelta(seconds=30)
    assert not qu.playing
    assert qu.current
    assert qu.current.track_id == 'Track4'
    qu.play(immediate=True)
    assert qu.playing
    assert qu.playing.track_id == 'Track4'
    qu._now += datetime.timedelta(seconds=30)
    assert qu.playing.track_id == 'Track4'
    qu.add(QueueItem('Track5', ONE_MINUTE, 'TestSession5', 'test_name'))
    assert qu.last
    assert qu.last.track_id == 'Track5'
    assert qu.last.start_time
    assert qu.last.start_time > qu.now
    qu._now += datetime.timedelta(seconds=60)
    assert  qu.playing.track_id == 'Track5'
    qu._now += datetime.timedelta(seconds=60)
    assert not qu.playing

def test_queue_stop(qu: Queue):
    assert qu._now
    qu.add(QueueItem('Track6', ONE_MINUTE, 'TestSession6', 'test_name'))
    qu.add(QueueItem('Track7', ONE_MINUTE, 'TestSession7', 'test_name'))
    assert not qu.playing
    qu._now += datetime.timedelta(seconds=60)
    assert not qu.playing
    qu.play(immediate=True)
    qu._now += datetime.timedelta(seconds=30)
    assert qu.playing
    assert qu.playing.track_id == 'Track6'
    qu.stop()
    assert not qu.playing
    assert all([i.start_time for i in qu.past])

    assert [i.start_time for i in qu.future] == [None, None]
    qu._now += datetime.timedelta(seconds=60)
    assert not qu.playing
    assert [i.track_id for i in qu.future] == ['Track6', 'Track7']
    qu.play(immediate=True)
    qu._now += datetime.timedelta(seconds=30)
    assert qu.playing
    assert qu.playing.track_id == 'Track6'
    qu._now += datetime.timedelta(seconds=60)
    assert qu.playing.track_id == 'Track7'
    qu._now += datetime.timedelta(seconds=60)
    assert not qu.playing

def test_queue_end_time(qu: Queue):
    assert qu._now
    qu.add(QueueItem('Track1', ONE_MINUTE, 'TestSession1', 'test_name'))
    qu.add(QueueItem('Track2', ONE_MINUTE, 'TestSession2', 'test_name'))
    qu.play(immediate=True)
    qu._now += datetime.timedelta(seconds=150)
    assert qu.end_time == qu.last.end_time       # type: ignore
    qu.add(QueueItem('Track3', ONE_MINUTE, 'TestSession3', 'test_name'))
    qu.add(QueueItem('Track4', ONE_MINUTE, 'TestSession4', 'test_name'))
    assert qu.end_time == qu.now + (datetime.timedelta(seconds=60)*2) + (qu.track_space*2)

def test_queue_seek_forwards(qu: Queue):
    qu.add(QueueItem('Track1', ONE_MINUTE, 'TestSession1', 'test_name'))
    qu.add(QueueItem('Track2', ONE_MINUTE, 'TestSession2', 'test_name'))
    qu.play(immediate=True)
    assert qu.items[0].start_time == qu.now
    assert qu.items[1].start_time == qu.now + datetime.timedelta(seconds=60) + qu.track_space
    # Seeking to the middle of a track moves everything by the exact amount
    qu.seek_forwards(20)
    assert qu.items[0].start_time == qu.now - datetime.timedelta(seconds=20)
    assert qu.items[1].start_time == qu.now + datetime.timedelta(seconds=60) + qu.track_space - datetime.timedelta(seconds=20)
    # If we seek past the end of a track, snap to the end of that track
    qu.seek_forwards(9001)
    assert qu.items[0].start_time == qu.now - datetime.timedelta(seconds=60)
    assert qu.items[1].start_time == qu.now + qu.track_space
    # Seeking to the middle of track space moves everything by the exact amount
    qu.seek_forwards(5)
    assert qu.items[1].start_time == qu.now + qu.track_space - datetime.timedelta(seconds=5)
    # If we seek past the end of track space, snap to the start of the next track
    qu.seek_forwards(420)
    assert qu.items[1].start_time == qu._now

def test_queue_seek_backwards(qu: Queue):
    qu.add(QueueItem('Track1', ONE_MINUTE, 'TestSession1', 'test_name'))
    qu.add(QueueItem('Track2', ONE_MINUTE, 'TestSession2', 'test_name'))
    qu.play(immediate=True)
    # Starting from the middle of space between tracks
    qu._now += datetime.timedelta(seconds=60) + qu.track_space/2  # type: ignore
    assert qu.items[0].start_time == qu.now - datetime.timedelta(seconds=60) - qu.track_space/2
    assert qu.items[1].start_time == qu.now + qu.track_space/2
    # Seeking backward within track space should move exactly, without adjusting past tracks
    qu.seek_backwards(1)
    assert qu.items[0].start_time == qu.now - datetime.timedelta(seconds=60) - qu.track_space/2
    assert qu.items[1].start_time == qu.now + datetime.timedelta(seconds=1) + qu.track_space/2
    # Seeking backwards past the start of space should go to the start of the space
    qu.seek_backwards(1234)
    assert qu.items[0].start_time == qu.now - datetime.timedelta(seconds=60) - qu.track_space/2
    assert qu.items[1].start_time == qu.now + qu.track_space
    # From the middle of a track
    qu._now += qu.track_space + datetime.timedelta(seconds=30)  # type: ignore
    # Seeking backward within track should move exactly, without adjusting past tracks
    qu.seek_backwards(10)
    assert qu.items[0].start_time == qu.now - datetime.timedelta(seconds=90) - qu.track_space*1.5
    assert qu.items[1].start_time == qu.now - datetime.timedelta(seconds=20)
    # Seeking backwards past the start of track should go to the start of the track
    qu.seek_backwards(1234)
    assert qu.items[0].start_time == qu.now - datetime.timedelta(seconds=90) - qu.track_space*1.5
    assert qu.items[1].start_time == qu.now

def test_queue_get(qu: Queue):
    # .get(id)
    track10 = QueueItem('Track10', ONE_MINUTE, 'TestSession10', 'test_name')
    qu.add(track10)
    index, queue_item = qu.get(track10.id)
    assert queue_item
    assert queue_item.track_id == 'Track10'

def test_queue_move(qu: Queue):
    assert qu._now
    t1 = QueueItem('Track11', ONE_MINUTE, 'TestSession11', 'test_name')
    t2 = QueueItem('Track12', ONE_MINUTE, 'TestSession12', 'test_name')
    t3 = QueueItem('Track13', ONE_MINUTE, 'TestSession13', 'test_name')
    t4 = QueueItem('Track14', ONE_MINUTE, 'TestSession14', 'test_name')
    qu.add(t1)
    qu.add(t2)
    qu.add(t3)
    qu.add(t4)
    assert qu.items == [t1,t2,t3,t4]

    qu.move(t3.id, t1.id)
    assert qu.items == [t3,t1,t2,t4]

    qu.move(t4.id, t3.id)
    assert qu.items == [t4,t3,t1,t2]

    qu.move(t3.id, -1)
    assert qu.items == [t4,t1,t2,t3]

    qu.play(immediate=True)
    qu._now += datetime.timedelta(seconds=60 * 5)
    with pytest.raises(AssertionError) as exc_info:
        qu.move(t4.id, t3.id)

