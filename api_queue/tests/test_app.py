import pytest
import collections.abc

# https://sanic.dev/en/plugins/sanic-testing/getting-started.html#basic-usage
@pytest.mark.asyncio
async def test_basic_asgi_client(app):  # mock_redis,
    #mock_redis.get.side_effect = ['foo',]

    request, response = await app.asgi_client.get("/")

    #assert request.method.lower() == "get"
    #assert response.body == b"foo"
    #assert response.status == 200


@pytest.mark.asyncio
async def test_tracks(app):
    request, response = await app.asgi_client.get("/queue/test/tracks.json")
    assert 'KAT_TUN_Your_side_Instrumental_' in response.json.keys()

@pytest.mark.asyncio
async def test_queue_null(app):
    request, response = await app.asgi_client.get("/queue/test/queue.json")
    assert isinstance(response.json, collections.abc.Sequence)

@pytest.mark.asyncio
async def test_queue_settings_default(app):
    request, response = await app.asgi_client.get("/queue/test/settings.json")
    assert isinstance(response.json, collections.abc.Mapping)
    assert 'track_space' in response.json
