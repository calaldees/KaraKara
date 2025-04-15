import pytest

import datetime

from api_queue.queue_model import QueueItem
from api_queue.queue_validation import validate_queue, QueueValidationError


ONE_MINUTE = datetime.timedelta(seconds=60)


def test_empty_queue(qu):
    validate_queue(qu)

def test_single_item(qu):
    qu.add(QueueItem('Track1', ONE_MINUTE, 'TestSession1', 'test_name'))
    validate_queue(qu)

def test_start_time(qu):
    qu.settings.validation_event_start_datetime += datetime.timedelta(hours=1)
    qu.add(QueueItem('Track1', ONE_MINUTE, 'TestSession1', 'test_name'))
    with pytest.raises(QueueValidationError, match='starts'):
        validate_queue(qu)

def test_end_time(qu):
    qu.settings.validation_event_end_datetime += datetime.timedelta(hours=-1)
    qu.add(QueueItem('Track1', ONE_MINUTE, 'TestSession1', 'test_name'))
    with pytest.raises(QueueValidationError, match='is full'):
        validate_queue(qu)

def test_performer_names(qu):
    qu.settings.validation_performer_names = ['TTT']
    qu.add(QueueItem('Track1', ONE_MINUTE, 'TestSession1', 'test_name'))
    with pytest.raises(QueueValidationError, match='test_name'):
        validate_queue(qu)

@pytest.mark.xfail(raises=NotImplementedError)
def test_duplicate_performer(qu):
    qu.add(QueueItem('Track1', ONE_MINUTE, 'TestSession1', 'test_name1'))
    qu.add(QueueItem('Track2', ONE_MINUTE, 'TestSession1', 'test_name1'))
    validate_queue(qu)

@pytest.mark.xfail(raises=NotImplementedError)
def test_duplicate_track(qu):
    qu.add(QueueItem('Track1', ONE_MINUTE, 'TestSession1', 'test_name1'))
    qu.add(QueueItem('Track1', ONE_MINUTE, 'TestSession1', 'test_name2'))
    validate_queue(qu)
