import pytest

import datetime
from api_queue.queue import Queue, QueueItem, QueueManagerCSV, SettingsManager


@pytest.fixture
def qu():
    qu = Queue([], track_space=datetime.timedelta(seconds=10))
    qu._now = datetime.datetime.now()
    return qu

def test_queue(qu):
    assert not qu.current
    assert not qu.playing

    qu.add(QueueItem('Track1', 60, 'TestSession1'))
    assert [i.track_id for i in qu.items] == ['Track1']
    assert qu.current.track_id == 'Track1'
    assert not qu.current.start_time
    qu.add(QueueItem('Track2', 60, 'TestSession2'))
    assert [i.track_id for i in qu.items] == ['Track1', 'Track2']
    assert qu.current.track_id == 'Track1'

    # Playing state when moving time forward
    qu.play()
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

    # Past tracks
    assert [i.track_id for i in qu.items] == ['Track1', 'Track2']
    assert [i.track_id for i in qu.past] == ['Track1', 'Track2']
    assert [i.track_id for i in qu.future] == []

    # Adding + Deleting + Future + current tracks work after played past tracks
    qu.add(QueueItem('Track3', 60, 'TestSession3'))
    qu.add(QueueItem('Track4', 60, 'TestSession4'))
    assert not qu.playing
    assert qu.current.track_id == 'Track3'
    assert [i.track_id for i in qu.future] == ['Track3', 'Track4']
    qu.delete(qu.current.id)
    assert [i.track_id for i in qu.future] == ['Track4']
    assert qu.current.track_id == 'Track4'

    # Can't delete past items
    assert [i.track_id for i in qu.past] == ['Track1', 'Track2']
    past_track_id = [i for i in qu.past][1].id
    qu.delete(past_track_id)
    assert [i.track_id for i in qu.past] == ['Track1', 'Track2']

    # Adding tracks while playing populates the start_time
    qu._now += datetime.timedelta(seconds=30)
    assert not qu.playing
    assert qu.current.track_id == 'Track4'
    qu.play()
    assert qu.playing.track_id == 'Track4'
    qu._now += datetime.timedelta(seconds=30)
    assert qu.playing.track_id == 'Track4'
    qu.add(QueueItem('Track5', 60, 'TestSession5'))
    assert qu.last.track_id == 'Track5'
    assert qu.last.start_time > qu.now
    qu._now += datetime.timedelta(seconds=60)
    assert  qu.playing.track_id == 'Track5'
    qu._now += datetime.timedelta(seconds=60)
    assert not qu.playing

    # Stop functions correctly
    qu.add(QueueItem('Track6', 60, 'TestSession6'))
    qu.add(QueueItem('Track7', 60, 'TestSession7'))
    assert not qu.playing
    qu._now += datetime.timedelta(seconds=60)
    assert not qu.playing
    qu.play()
    qu._now += datetime.timedelta(seconds=30)
    assert qu.playing.track_id == 'Track6'
    qu.stop()
    assert not qu.playing
    assert all([i.start_time for i in qu.past])

    assert [i.start_time for i in qu.future] == [None, None]
    qu._now += datetime.timedelta(seconds=60)
    assert not qu.playing
    assert [i.track_id for i in qu.future] == ['Track6', 'Track7']
    qu.play()
    qu._now += datetime.timedelta(seconds=30)
    assert qu.playing.track_id == 'Track6'
    qu._now += datetime.timedelta(seconds=60)
    assert qu.playing.track_id == 'Track7'
    qu._now += datetime.timedelta(seconds=60)
    assert not qu.playing

    # .end_time
    last = qu.last
    assert qu.end_time == last.end_time
    qu.add(QueueItem('Track8', 60, 'TestSession8'))
    qu.add(QueueItem('Track9', 60, 'TestSession9'))
    assert qu.end_time == qu.now + (datetime.timedelta(seconds=60)*2) + (qu.track_space*2)

    # TODO: try to break this test up .. I originally made it as a doctest and it got too big


def test_queue_get(qu):
    # .get(id)
    track10 = QueueItem('Track10', 60, 'TestSession10')
    qu.add(track10)
    index, queue_item = qu.get(track10.id)
    assert queue_item.track_id == 'Track10'

def test_queue_move(qu):
    t1 = QueueItem('Track11', 60, 'TestSession11')
    t2 = QueueItem('Track12', 60, 'TestSession12')
    t3 = QueueItem('Track13', 60, 'TestSession13')
    t4 = QueueItem('Track14', 60, 'TestSession14')
    qu.add(t1)
    qu.add(t2)
    qu.add(t3)
    qu.add(t4)
    assert qu.items == [t1,t2,t3,t4]
    
    qu.move(t3.id, t1.id)
    assert qu.items == [t3,t1,t2,t4]

    qu.move(t4.id, t3.id)
    assert qu.items == [t4,t3,t1,t2]

    qu.move(t3.id, 1)
    assert qu.items == [t4,t1,t2,t3]

    qu.play()
    qu._now += datetime.timedelta(seconds=60 * 5)
    with pytest.raises(AssertionError) as exc_info:
        qu.move(t4.id, t3.id)


def test_queue_manager():
    # TODO: finish
    manager = QueueManagerCSV(settings=SettingsManager())
    with manager.queue_modify_context('test') as qu:
        qu.add(QueueItem('Track6', 60, 'TestSession6'))
