import pytest
from unittest.mock import patch, AsyncMock

import pathlib
import shutil
from urllib.parse import urlencode

try:
    import ujson as json
except ImportError:
    import json


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
            'TRACKS': temp_path_tracks,
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
    async def queue(self):
        request, response = await self.app.asgi_client.get(f"/queue/{self._queue}/queue.json")
        return response.json
    @property
    async def tracks(self):
        request, response = await self.app.asgi_client.get(f"/queue/{self._queue}/tracks.json")
        return response.json
    @property
    async def settings(self):
        request, response = await self.app.asgi_client.get(f"/queue/{self._queue}/settings.json")
        return response.json

    async def post(self, **kwargs):
        request, response = await self.app.asgi_client.post(f"/queue/{self._queue}/", data=json.dumps(kwargs))
        return response
    async def delete(self, **kwargs):
        request, response = await self.app.asgi_client.delete(f"/queue/{self._queue}/?{urlencode(kwargs)}")
        return response
    async def put(self, **kwargs):
        request, response = await self.app.asgi_client.put(f"/queue/{self._queue}/?{urlencode(kwargs)}")
        return response

    async def command(self, command):
        request, response = await self.app.asgi_client.get(f"/queue/{self._queue}/command/{command}")
        return response



@pytest.fixture
def queue_model(app):
    return QueueModel(app, 'test')
