import pytest

from api_queue.queue_model import QueueItem
from api_queue.queue_manager import QueueManagerCSV, SettingsManager


# TODO: more queue_manager tests needed

@pytest.mark.skip()
def test_queue_manager():
    # TODO: finish
    manager = QueueManagerCSV(settings=SettingsManager())
    with manager.queue_modify_context('test') as qu:
        qu.add(QueueItem('Track6', 60, 'TestSession6', 'test_name'))
