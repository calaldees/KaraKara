import pytest
from unittest.mock import MagicMock
import datetime

from api_queue.settings_manager import SettingsManager
from api_queue.queue_model import Queue, QueueItem
from api_queue.queue_validation import default as default_validation

@pytest.fixture
def qu():
    mock_settings_manager = MagicMock()
    mock_settings_manager.get_json.return_value = {
        "track_space": 10.0,
        "validation_event_start_datetime": '2022-01-01T09:50:00.000000',
        "validation_event_end_datetime": '2022-01-01T10:10:00.000000',
        "validation_duplicate_performer_timedelta": '4min',
        "validation_duplicate_track_timedelta": '4min',
        "validation_performer_names": [],
    }
    qu = Queue([], settings=SettingsManager.get(mock_settings_manager, 'test'))
    qu._now = datetime.datetime(2022, 1, 1, 10, 0, 0)
    return qu


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
    assert 'ending' in default_validation(qu)

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
