import pytest
import collections.abc as ct
from unittest.mock import AsyncMock
from pathlib import Path

import api_queue.server
from api_queue.settings_manager import QueueSettings
from api_queue.queue_model import Queue
from api_queue.api_types import App

import datetime
import pathlib
import shutil


@pytest.fixture
def mock_mqtt():
    return AsyncMock()


@pytest.fixture
async def app(tmp_path: Path, mock_mqtt) -> ct.AsyncGenerator[App]:
    test_path_tracks = pathlib.Path(__file__).parent.joinpath("tracks.json")
    temp_path_tracks = tmp_path.joinpath("tracks.json")
    shutil.copy(test_path_tracks, temp_path_tracks)

    app = api_queue.server.app
    app.config.update(
        {
            "PATH_TRACKS": temp_path_tracks,
            "PATH_QUEUE": tmp_path,
            "MQTT": mock_mqtt,
            "BACKGROUND_TASK_TRACK_UPDATE_ENABLED": False,
        }
    )
    yield app


@pytest.fixture
def qu() -> Queue:
    settings = QueueSettings(
        track_space=datetime.timedelta(seconds=10),
        validation_event_start_datetime=datetime.datetime(2022, 1, 1, 9, 50, tzinfo=datetime.timezone.utc),
        validation_event_end_datetime=datetime.datetime(2022, 1, 1, 10, 10, tzinfo=datetime.timezone.utc),
        # validation_duplicate_performer_timedelta = datetime.timedelta(minutes=4),
        # validation_duplicate_track_timedelta = datetime.timedelta(minutes=4),
        validation_performer_names=[],
        coming_soon_track_count=3,
    )
    qu = Queue([], settings=settings)
    qu._now = datetime.datetime(2022, 1, 1, 10, 0, 0, tzinfo=datetime.timezone.utc)
    return qu
