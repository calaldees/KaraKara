import pytest
from unittest.mock import patch, AsyncMock


#@pytest.fixture
#async def mock_redis():
#    import api_queue.server
#    with patch.object(api_queue.server.aioredis, 'from_url', side_effect=AsyncMock()) as mock_redis:
#        yield await mock_redis()


@pytest.fixture
async def app(mock_redis):
    # get the single registered app - is this needed? can we just import app from server?
    #from sanic import Sanic
    #app = Sanic.get_app()

    import api_queue.server
    yield api_queue.server.app
