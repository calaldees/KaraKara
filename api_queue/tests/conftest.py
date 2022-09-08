import pytest
from unittest.mock import patch, AsyncMock

import pathlib
import shutil
import json
from urllib.parse import urlencode


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
            'path_queue': tmp_path,
            'MQTT': mock_mqtt,
        }
    )
    yield app

class QueueModel():
    def __init__(self, app, queue):
        self.app = app
        self._queue = queue
        self.session_id = None
    @property
    def cookies(self):
        if self.session_id:
            return {'session_id': self.session_id}
        return {}
    @property
    async def queue(self):
        request, response = await self.app.asgi_client.get(f"/queue/{self._queue}/queue.json", cookies=self.cookies)
        return response.json
    @property
    async def tracks(self):
        request, response = await self.app.asgi_client.get(f"/queue/{self._queue}/tracks.json", cookies=self.cookies)
        return response.json
    @property
    async def settings(self):
        request, response = await self.app.asgi_client.get(f"/queue/{self._queue}/settings.json", cookies=self.cookies)
        return response.json
    async def add(self, **kwargs):
        request, response = await self.app.asgi_client.post(f"/queue/{self._queue}/", data=json.dumps(kwargs), cookies=self.cookies)
        return response
    async def delete(self, **kwargs):
        request, response = await self.app.asgi_client.delete(f"/queue/{self._queue}/?{urlencode(kwargs)}", cookies=self.cookies)
        return response


@pytest.fixture
def queue_model(app):
    return QueueModel(app, 'test')
