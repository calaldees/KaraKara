import pytest
import collections.abc
import json

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

@pytest.mark.asyncio
async def test_queue_add(app):
    # queue is empty
    request, response = await app.asgi_client.get("/queue/test/queue.json")
    assert len(response.json) == 0

    # reject add tracks that are not in track list
    request, response = await app.asgi_client.post("/queue/test/", data=json.dumps(
        {'track_id': 'NotRealTrackId', 'performer_name':'test'}
    ))
    assert response.status == 400

    # add track
    request, response = await app.asgi_client.post("/queue/test/", data=json.dumps(
        {'track_id': 'KAT_TUN_Your_side_Instrumental_', 'performer_name':'test'}
    ))
    assert response.status == 200
    # check track now in queue
    request, response = await app.asgi_client.get("/queue/test/queue.json")
    assert len(response.json) == 1
    assert {'track_id': 'KAT_TUN_Your_side_Instrumental_', 'performer_name':'test'}.items() <= response.json[0].items()
