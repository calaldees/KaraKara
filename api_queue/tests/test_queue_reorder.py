import pytest
from unittest.mock import patch
import datetime

from api_queue.queue_model import QueueItem
from api_queue.queue_reorder import reorder, _rank


def _QueueItem(*args, added_time=datetime.datetime(2022, 1, 1, 10, 0, 0, tzinfo=datetime.timezone.utc), **kwargs):
    with patch('api_queue.queue_model.datetime') as mock_datetime:
        mock_datetime.datetime.now.return_value = added_time
        return QueueItem(*args, **kwargs)

def _mins_ago(minutes):
    return datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(minutes=minutes)


@pytest.fixture
def qu(qu):
    qu._now = None
    qu.settings["coming_soon_track_count"] = 3
    return qu


def test_empty_reorder(qu):
    reorder(qu)

def test_no_reorder__tracks_within_coming_soon_track_count(qu):
    qu.add(QueueItem('Track1', 60, 'TestSession1', 'test_name1', added_time=_mins_ago(60)))
    qu.add(QueueItem('Track2', 60, 'TestSession2', 'test_name2', added_time=_mins_ago(50)))
    qu.add(QueueItem('Track3', 60, 'TestSession3', 'test_name3', added_time=_mins_ago(40)))
    reorder(qu)
    assert [i.track_id for i in qu.future] == ['Track1','Track2','Track3']

def test_no_reorder(qu):
    """
    no_reorder - 6 tracks queued by 6 different people
    """
    qu.add(QueueItem('Track1', 60, 'TestSession1', 'test_name1', added_time=_mins_ago(60)))
    qu.add(QueueItem('Track2', 60, 'TestSession2', 'test_name2', added_time=_mins_ago(50)))
    qu.add(QueueItem('Track3', 60, 'TestSession3', 'test_name3', added_time=_mins_ago(40)))
    qu.add(QueueItem('Track4', 60, 'TestSession1', 'test_name4', added_time=_mins_ago(30)))
    qu.add(QueueItem('Track5', 60, 'TestSession2', 'test_name5', added_time=_mins_ago(20)))
    qu.add(QueueItem('Track6', 60, 'TestSession3', 'test_name6', added_time=_mins_ago(10)))
    reorder(qu)
    assert [i.track_id for i in qu.future] == ['Track1','Track2','Track3','Track4','Track5','Track6']


def test_no_reorder_protect_coming_soon_track_count(qu):
    qu.add(QueueItem('Track1', 60, 'TestSession1', 'test_name1', added_time=_mins_ago(60), start_time=_mins_ago(10)))
    qu.add(QueueItem('Track2', 60, 'TestSession2', 'test_name2', added_time=_mins_ago(50), start_time=_mins_ago( 5)))
    qu.add(QueueItem('Track3', 60, 'TestSession3', 'test_name3', added_time=_mins_ago(40)))
    qu.add(QueueItem('Track4', 60, 'TestSession1', 'test_name4', added_time=_mins_ago(30)))
    qu.add(QueueItem('Track11', 60, 'TestSession1', 'test_name1', added_time=_mins_ago(20)))  # test_name1 has sung before and should be outranked by all the others ... BUT it is currently in the protected 'coming_soon_track_count'
    qu.add(QueueItem('Track5', 60, 'TestSession3', 'test_name5', added_time=_mins_ago(10)))
    reorder(qu)
    assert [i.track_id for i in qu.future] == ['Track3','Track4','Track11',  'Track5']

def test_reorder_1(qu):
    qu.add(QueueItem('Track1', 60, 'TestSession1', 'test_name1', added_time=_mins_ago(60), start_time=_mins_ago(10)))
    qu.add(QueueItem('Track2', 60, 'TestSession2', 'test_name2', added_time=_mins_ago(50), start_time=_mins_ago( 5)))
    qu.add(QueueItem('Track3', 60, 'TestSession3', 'test_name3', added_time=_mins_ago(40)))
    qu.add(QueueItem('Track4', 60, 'TestSession1', 'test_name4', added_time=_mins_ago(30)))
    qu.add(QueueItem('Track5', 60, 'TestSession3', 'test_name5', added_time=_mins_ago(20)))
    qu.add(QueueItem('Track11', 60, 'TestSession1', 'test_name1', added_time=_mins_ago(20)))  # test_name1(Track11) has sung before and should be outranked by all the others - Track11 should be last in queue
    qu.add(QueueItem('Track6', 60, 'TestSession6', 'test_name6', added_time=_mins_ago(10)))
    reorder(qu)
    assert [i.track_id for i in qu.future] == ['Track3','Track4','Track5', 'Track6','Track11']


def test_reorder_multiple_items_in_queue(qu):
    """
    `test_name1` has two tracks in the queue (Track1 and Track11) - the second track (Track11) should be last in the queue
    """
    qu.add(QueueItem('Track1', 60, 'TestSession1', 'test_name1', added_time=_mins_ago(60)))
    qu.add(QueueItem('Track2', 60, 'TestSession2', 'test_name2', added_time=_mins_ago(50)))
    qu.add(QueueItem('Track3', 60, 'TestSession3', 'test_name3', added_time=_mins_ago(40)))
    qu.add(QueueItem('Track4', 60, 'TestSession3', 'test_name4', added_time=_mins_ago(40)))
    qu.add(QueueItem('Track11', 60, 'TestSession1', 'test_name1', added_time=_mins_ago(30)))  
    qu.add(QueueItem('Track5', 60, 'TestSession2', 'test_name5', added_time=_mins_ago(20)))
    qu.add(QueueItem('Track6', 60, 'TestSession3', 'test_name6', added_time=_mins_ago(10)))
    reorder(qu)
    # While both Track1+Track11 are speculative, the order will not change
    assert [i.track_id for i in qu.future] == ['Track1','Track2','Track3','Track4','Track11','Track5','Track6']
    # but when Track1 is played, it detects that `test_name1` has sung before and bumps Track11 down the list
    qu.items[0].start_time = _mins_ago( 5)
    reorder(qu)
    assert [i.track_id for i in qu.future] == ['Track2','Track3','Track4','Track5','Track6','Track11']
