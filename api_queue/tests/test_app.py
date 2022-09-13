import pytest
import collections.abc

try:
    import ujson as json
except ImportError:
    import json



@pytest.mark.asyncio
async def test_root(app):  # mock_redis,
    request, response = await app.asgi_client.get("/")
    assert response.status == 302


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
    response = await queue_model.post()
    assert response.status == 400
    response = await queue_model.post(track_id='NotRealTrackId', performer_name='test')
    assert response.status == 400

    mock_mqtt.publish.assert_not_awaited()
    # add track
    response = await queue_model.post(track_id='KAT_TUN_Your_side_Instrumental_', performer_name='test')
    assert response.status == 200
    mock_mqtt.publish.assert_awaited_once()
    # check track now in queue
    queue = await queue_model.queue
    assert len(queue) == 1
    assert {'track_id': 'KAT_TUN_Your_side_Instrumental_', 'performer_name':'test'}.items() <= queue[0].items()
    assert mock_mqtt.publish.await_args.args == ("room/test/queue", json.dumps(queue))
    assert mock_mqtt.publish.await_args.kwargs == dict(retain=True)

@pytest.mark.asyncio
async def test_queue_delete(queue_model, mock_mqtt):
    # populate queue
    assert len(await queue_model.queue) == 0
    await queue_model.post(track_id='KAT_TUN_Your_side_Instrumental_', performer_name='test1')
    await queue_model.post(track_id='Animaniacs_OP', performer_name='test2')
    queue = await queue_model.queue
    assert len(queue) == 2

    # try to delete invalid
    mock_mqtt.publish.reset_mock()
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

    # session_id owner reject
    queue_model.session_id = 'not_real'
    response = await queue_model.delete(queue_item_id=queue[0]['id'])
    response.status == 403

    # session_id admin can delete
    queue_model.session_id = 'admin'
    response = await queue_model.delete(queue_item_id=queue[0]['id'])
    response.status == 200
    queue = await queue_model.queue
    assert len(queue) == 0

@pytest.mark.asyncio
async def test_queue_move(queue_model, mock_mqtt):
    # populate queue
    await queue_model.post(track_id='KAT_TUN_Your_side_Instrumental_', performer_name='test1')
    await queue_model.post(track_id='Animaniacs_OP', performer_name='test2')
    await queue_model.post(track_id='Macross_Dynamite7_OP_Dynamite_Explosion', performer_name='test3')
    queue = await queue_model.queue
    assert len(queue) == 3

    # invalid moves
    mock_mqtt.publish.reset_mock()
    response = await queue_model.put()
    assert response.status == 400
    response = await queue_model.put(queue_item_id_1=0, queue_item_id_2=0)
    assert response.status == 403
    queue_model.session_id = 'admin'
    response = await queue_model.put(queue_item_id_1=0, queue_item_id_2=0)
    assert response.status == 400
    mock_mqtt.publish.assert_not_awaited()

    # move
    response = await queue_model.put(queue_item_id_1=queue[0]['id'], queue_item_id_2=queue[2]['id'])
    assert response.status == 201
    mock_mqtt.publish.assert_awaited_once()
    queue = await queue_model.queue
    assert [i['track_id'] for i in queue] == ['Animaniacs_OP', 'KAT_TUN_Your_side_Instrumental_', 'Macross_Dynamite7_OP_Dynamite_Explosion']
    # move to end
    response = await queue_model.put(queue_item_id_1=queue[0]['id'], queue_item_id_2=1)
    queue = await queue_model.queue
    assert [i['track_id'] for i in queue] == ['KAT_TUN_Your_side_Instrumental_', 'Macross_Dynamite7_OP_Dynamite_Explosion', 'Animaniacs_OP']

@pytest.mark.asyncio
async def test_queue_command(queue_model, mock_mqtt):
    # populate tracks
    await queue_model.post(track_id='KAT_TUN_Your_side_Instrumental_', performer_name='test1')
    await queue_model.post(track_id='Animaniacs_OP', performer_name='test2')
    await queue_model.post(track_id='Macross_Dynamite7_OP_Dynamite_Explosion', performer_name='test3')
    queue = await queue_model.queue
    assert not any(queue_item['start_time'] for queue_item in queue), 'no tracks should have a start time'

    # invalid commands
    mock_mqtt.publish.reset_mock()
    response = await queue_model.command('play')
    assert response.status == 403
    queue_model.session_id = 'admin'
    response = await queue_model.command('not_real_command')
    assert response.status == 404
    mock_mqtt.publish.assert_not_awaited()

    # play
    response = await queue_model.command('play')
    assert response.status == 200
    mock_mqtt.publish.assert_awaited_once()

    queue = await queue_model.queue
    assert all(queue_item['start_time'] for queue_item in queue), 'all tracks should have a start time'

    # stop
    response = await queue_model.command('stop')
    assert response.status == 200
    queue = await queue_model.queue
    assert not any(queue_item['start_time'] for queue_item in queue), 'no tracks should have a start time'
