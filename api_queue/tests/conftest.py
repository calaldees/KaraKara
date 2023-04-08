import pytest
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
async def app(tmp_path, mock_mqtt):  #mock_redis
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
        }
    )
    yield app

class QueueModel():
    def __init__(self, app, queue):
        self.app = app
        self._queue = queue
        del self.session_id

    @property
    def session_id(self):
        return self.app.asgi_client.cookies.get('session_id')
    @session_id.setter
    def session_id(self, value):
        self.app.asgi_client.cookies.delete('session_id')
        self.app.asgi_client.cookies.set('session_id', value)
    @session_id.deleter
    def session_id(self):
        self.app.asgi_client.cookies.delete('session_id')

    @property
    async def queue_csv(self):
        request, response = await self.app.asgi_client.get(f"/room/{self._queue}/queue.csv")
        return response.text
    @property
    async def queue(self):
        request, response = await self.app.asgi_client.get(f"/room/{self._queue}/queue.json")
        return response.json
    @property
    async def tracks(self):
        request, response = await self.app.asgi_client.get(f"/room/{self._queue}/tracks.json")
        return response.json
    @property
    async def settings(self):
        request, response = await self.app.asgi_client.get(f"/room/{self._queue}/settings.json")
        return response.json

    async def settings_put(self, payload):
        request, response = await self.app.asgi_client.put(f"/room/{self._queue}/settings.json", data=json.dumps(payload))
        return response
    async def post(self, **kwargs):
        request, response = await self.app.asgi_client.post(f"/room/{self._queue}/queue.json", data=json.dumps(kwargs))
        return response
    async def delete(self, queue_item_id):
        request, response = await self.app.asgi_client.delete(f"/room/{self._queue}/queue/{queue_item_id}.json")
        return response
    async def put(self, **kwargs):
        request, response = await self.app.asgi_client.put(f"/room/{self._queue}/queue.json", data=json.dumps(kwargs))
        return response

    async def command(self, command):
        request, response = await self.app.asgi_client.get(f"/room/{self._queue}/command/{command}.json")
        return response



@pytest.fixture
def queue_model(app):
    return QueueModel(app, 'test')


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
        "coming_soon_track_count": 3,
    }
    qu = Queue([], settings=SettingsManager.get(mock_settings_manager, 'test'))
    qu._now = datetime.datetime(2022, 1, 1, 10, 0, 0)
    return qu
