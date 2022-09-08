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
async def test_tracks(queue_model):
    assert 'KAT_TUN_Your_side_Instrumental_' in (await queue_model.tracks).keys()

@pytest.mark.asyncio
async def test_queue_null(queue_model):
    assert isinstance(await queue_model.queue, collections.abc.Sequence)

@pytest.mark.asyncio
async def test_queue_settings_default(queue_model):
    settings = await queue_model.settings
    assert isinstance(settings, collections.abc.Mapping)
    assert 'track_space' in settings

@pytest.mark.asyncio
async def test_queue_add(queue_model, mock_mqtt):
    # queue is empty
    assert len(await queue_model.queue) == 0

    # reject add tracks that are not in track list
    response = await queue_model.add()
    assert response.status == 400
    response = await queue_model.add(track_id='NotRealTrackId', performer_name='test')
    assert response.status == 400

    mock_mqtt.publish.assert_not_awaited()
    # add track
    response = await queue_model.add(track_id='KAT_TUN_Your_side_Instrumental_', performer_name='test')
    assert response.status == 200
    mock_mqtt.publish.assert_awaited_once()
    # check track now in queue
    queue = await queue_model.queue
    assert len(queue) == 1
    assert {'track_id': 'KAT_TUN_Your_side_Instrumental_', 'performer_name':'test'}.items() <= queue[0].items()
    assert mock_mqtt.publish.await_args.args == ("karakara/room/test/queue", tuple(queue))
    assert mock_mqtt.publish.await_args.kwargs == dict(retain=True)

@pytest.mark.asyncio
async def test_queue_delete(queue_model, mock_mqtt):
    # populate queue
    assert len(await queue_model.queue) == 0
    await queue_model.add(track_id='KAT_TUN_Your_side_Instrumental_', performer_name='test1')
    await queue_model.add(track_id='Animaniacs_OP', performer_name='test2')
    queue = await queue_model.queue
    assert len(queue) == 2

    # try to delete invalid
    mock_mqtt.publish.reset_mock()
    response = await queue_model.delete()
    assert response.status == 400
    response = await queue_model.delete(queue_item_id='NotReal')
    assert response.status == 400
    response = await queue_model.delete(queue_item_id=999)
    assert response.status == 404
    mock_mqtt.publish.assert_not_awaited()

    # delete
    response = await queue_model.delete(queue_item_id=queue[0]['id'])
    assert response.status == 200
    mock_mqtt.publish.assert_awaited_once()
    queue = await queue_model.queue
    assert len(queue) == 1
    assert queue[0]['track_id'] == 'Animaniacs_OP'
