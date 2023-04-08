from unittest.mock import patch
import datetime

from api_queue.queue_model import QueueItem
from api_queue.queue_reorder import reorder


def _QueueItem(*args, added_time=datetime.datetime(2022, 1, 1, 10, 0, 0), **kwargs):
    with patch('api_queue.queue_model.datetime') as mock_datetime:
        mock_datetime.datetime.now.return_value = added_time
        return QueueItem(*args, **kwargs)


def test_empty_reorder(qu):
    queue_item = _QueueItem('','','','')
    assert reorder(qu) is None
