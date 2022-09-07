import pytest
from unittest.mock import patch, AsyncMock

import pathlib
import shutil



#@pytest.fixture
#async def mock_redis():
#    import api_queue.server
#    with patch.object(api_queue.server.aioredis, 'from_url', side_effect=AsyncMock()) as mock_redis:
#        yield await mock_redis()


@pytest.fixture
async def app(tmp_path):  #mock_redis
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
            'DEBUG': True,
        }
    )
    yield app


