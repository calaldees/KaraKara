from unittest.mock import patch
import datetime

from api_queue.queue_model import QueueItem
from api_queue.queue_reorder import reorder


def _QueueItem(*args, added_time=datetime.datetime(2022, 1, 1, 10, 0, 0), **kwargs):
    with patch('api_queue.queue_model.datetime') as mock_datetime:
        mock_datetime.datetime.now.return_value = added_time
        return QueueItem(*args, **kwargs)


def test_empty_reorder(qu):
    assert reorder(qu) is None

def test_no_reorder(qu):
    qu.add(_QueueItem('Track1', 60, 'TestSession1', 'test_name1'))
    qu.add(_QueueItem('Track2', 60, 'TestSession2', 'test_name2'))
    qu.add(_QueueItem('Track3', 60, 'TestSession3', 'test_name3'))

    with patch('api_queue.queue_reorder.datetime') as mock_datetime:
        mock_datetime.datetime.now.return_value = datetime.datetime(2022, 1, 1, 10, 0, 0)
        assert reorder(qu) is None

    assert [i.track_id for i in qu.future] == ['Track1','Track2','Track3']
