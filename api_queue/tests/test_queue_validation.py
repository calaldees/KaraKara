import pytest

import datetime

from api_queue.queue_model import QueueItem
from api_queue.queue_validation import default as default_validation


def test_empty_queue(qu):
    assert default_validation(qu) is None

@pytest.mark.skip
def test_single_item(qu):
    qu.add(QueueItem('Track1', 60, 'TestSession1', 'test_name'))
    assert default_validation(qu) is None

def test_start_time(qu):
    qu.settings["validation_event_start_datetime"] += datetime.timedelta(hours=1)
    assert 'starts' in default_validation(qu)

def test_end_time(qu):
    qu.settings["validation_event_end_datetime"] += datetime.timedelta(hours=-1)
    assert 'is full' in default_validation(qu)

def test_performer_names(qu):
    qu.settings["validation_performer_names"] = ['TTT']
    qu.add(QueueItem('Track1', 60, 'TestSession1', 'test_name'))
    assert 'test_name' in default_validation(qu)

@pytest.mark.xfail(raises=NotImplementedError)
def test_duplicate_performer(qu):
    qu.add(QueueItem('Track1', 60, 'TestSession1', 'test_name1'))
    qu.add(QueueItem('Track2', 60, 'TestSession1', 'test_name1'))
    assert 'test_name1' in default_validation(qu)

@pytest.mark.xfail(raises=NotImplementedError)
def test_duplicate_track(qu):
    qu.add(QueueItem('Track1', 60, 'TestSession1', 'test_name1'))
    qu.add(QueueItem('Track1', 60, 'TestSession1', 'test_name2'))
    assert 'Track1' in default_validation(qu)
