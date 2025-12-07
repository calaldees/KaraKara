import datetime
from pathlib import Path

from api_queue.settings_manager import SettingsManager
from api_queue.queue_model import QueueItem
from api_queue.queue_manager import QueueManager


# TODO: more queue_manager tests needed


def test_queue_manager(tmp_path: Path):
    # TODO: finish
    manager = QueueManager(path=tmp_path, settings=SettingsManager(path=tmp_path))
    with manager.queue_modify_context("test") as qu:
        qu.add(
            QueueItem(
                track_id="Track6",
                track_duration=datetime.timedelta(seconds=60),
                session_id="abcd-1234-ghjk-5787",
                performer_name="test_name",
                video_variant="Default",
                subtitle_variant="Default",
            )
        )
    assert manager.for_json("test")[0]["session_id"] == "abcd"
