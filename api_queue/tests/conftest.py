import sanic
import pytest
import typing as t
from unittest.mock import patch, AsyncMock, MagicMock

from api_queue.settings_manager import SettingsManager
from api_queue.queue_model import Queue

import datetime
import pathlib
import shutil
from urllib.parse import urlencode

import ujson as json


#@pytest.fixture
#async def mock_redis():
#    import api_queue.server
#    with patch.object(api_queue.server.aioredis, 'from_url', side_effect=AsyncMock()) as mock_redis:
#        yield await mock_redis()

@pytest.fixture
def mock_mqtt():
    return AsyncMock()


@pytest.fixture
async def app(tmp_path, mock_mqtt) -> t.AsyncGenerator[sanic.Sanic]:
    # get the single registered app - is this needed? can we just import app from server?
    #from sanic import Sanic
    #app = Sanic.get_app()

    test_path_tracks = pathlib.Path(__file__).parent.joinpath('tracks.json')
    temp_path_tracks = tmp_path.joinpath('tracks.json')
    shutil.copy(test_path_tracks, temp_path_tracks)

    import api_queue.server
    app = api_queue.server.app
    app.config.update(
        {
            'PATH_TRACKS': temp_path_tracks,
            'PATH_QUEUE': tmp_path,
            'MQTT': mock_mqtt,
            'BACKGROUND_TASK_TRACK_UPDATE_ENABLED': False,
        }
    )
    yield app


@pytest.fixture
def qu() -> Queue:
    mock_settings_manager = MagicMock()
    mock_settings_manager.get_json.return_value = {
        "track_space": 10.0,
        "validation_event_start_datetime": '2022-01-01T09:50:00.000000',
        "validation_event_end_datetime": '2022-01-01T10:10:00.000000',
        "validation_duplicate_performer_timedelta": '4min',
        "validation_duplicate_track_timedelta": '4min',
        "validation_performer_names": [],
        "coming_soon_track_count": 3,
    }
    qu = Queue([], settings=SettingsManager.get(mock_settings_manager, 'test'))
    qu._now = datetime.datetime(2022, 1, 1, 10, 0, 0, tzinfo=datetime.timezone.utc)
    return qu
