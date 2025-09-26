import pytest
import datetime

from api_queue.settings_manager import SettingsManager
from api_queue.queue_model import QueueItem
from api_queue.queue_manager import QueueManagerCSV


# TODO: more queue_manager tests needed


@pytest.mark.skip()
def test_queue_manager():
    # TODO: finish
    manager = QueueManagerCSV(settings=SettingsManager())
    with manager.queue_modify_context("test") as qu:
        qu.add(
            QueueItem(
                track_id="Track6",
                track_duration=datetime.timedelta(seconds=60),
                session_id="TestSession6",
                performer_name="test_name",
            )
        )
