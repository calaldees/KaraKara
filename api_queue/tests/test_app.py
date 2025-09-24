import sanic
import pytest
import collections.abc
import datetime
import typing as t

import ujson as json


class APIQueue:
    def __init__(self, app: sanic.Sanic, queue: str):
        self.app = app
        self._queue = queue
        del self.session_id

    @property
    def session_id(self):
        return self.app.asgi_client.cookies.get("session_id")

    @session_id.setter
    def session_id(self, value: str):
        self.app.asgi_client.cookies.delete("session_id")
        self.app.asgi_client.cookies.set("session_id", value)

    @session_id.deleter
    def session_id(self):
        self.app.asgi_client.cookies.delete("session_id")

    @property
    async def queue_csv(self) -> str:
        request, response = await self.app.asgi_client.get(f"/room/{self._queue}/queue.csv")
        return response.text

    @property
    async def queue(self) -> t.Sequence[t.Mapping]:
        request, response = await self.app.asgi_client.get(f"/room/{self._queue}/queue.json")
        return response.json

    @property
    async def tracks(self):
        request, response = await self.app.asgi_client.get(f"/room/{self._queue}/tracks.json")
        return response.json

    @property
    async def settings(self) -> t.Mapping[str, t.Any]:
        request, response = await self.app.asgi_client.get(f"/room/{self._queue}/settings.json")
        return response.json

    async def settings_put(self, payload: t.Mapping[str, t.Any]):
        request, response = await self.app.asgi_client.put(
            f"/room/{self._queue}/settings.json", data=json.dumps(payload)
        )
        return response

    async def post(self, **kwargs):
        request, response = await self.app.asgi_client.post(f"/room/{self._queue}/queue.json", data=json.dumps(kwargs))
        return response

    async def delete(self, queue_item_id: int):
        request, response = await self.app.asgi_client.delete(f"/room/{self._queue}/queue/{queue_item_id}.json")
        return response

    async def put(self, **kwargs):
        request, response = await self.app.asgi_client.put(f"/room/{self._queue}/queue.json", data=json.dumps(kwargs))
        return response

    async def command(self, command: str):
        request, response = await self.app.asgi_client.get(f"/room/{self._queue}/command/{command}.json")
        return response


@pytest.fixture
def api_queue(app: sanic.Sanic):
    return APIQueue(app, "test")


@pytest.mark.asyncio
async def test_root(app: sanic.Sanic):  # mock_redis,
    request, response = await app.asgi_client.get("/")
    assert response.status == 302


@pytest.mark.asyncio
async def test_queue_invalid_name(app: sanic.Sanic):
    request, response = await app.asgi_client.get("/room/キ/queue.json")
    assert response.status == 404
    request, response = await app.asgi_client.get("/room/ /queue.json")
    assert response.status == 404
    request, response = await app.asgi_client.get("/room/queueNameIsFarFarFarFarFarFarToLong/queue.json")
    assert response.status == 404
    request, response = await app.asgi_client.get("/room/キ/queue.csv")
    assert response.status == 404


@pytest.mark.asyncio
async def test_tracks(api_queue: APIQueue):
    assert "KAT_TUN_Your_side_Instrumental" in (await api_queue.tracks).keys()


@pytest.mark.asyncio
async def test_queue_null(api_queue: APIQueue):
    assert isinstance(await api_queue.queue, collections.abc.Sequence)


@pytest.mark.asyncio
async def test_queue_settings_default(api_queue: APIQueue):
    settings = await api_queue.settings
    assert isinstance(settings, collections.abc.Mapping)
    assert "track_space" in settings


@pytest.mark.asyncio
async def test_queue_settings_change(api_queue: APIQueue, mock_mqtt):
    settings = await api_queue.settings
    assert settings["track_space"] == 15.0

    mock_mqtt.publish.assert_not_awaited()
    api_queue.session_id = "admin"
    response = await api_queue.settings_put(payload={"track_space": 10.0})
    assert response.status == 200
    mock_mqtt.publish.assert_awaited_once()

    settings = await api_queue.settings
    assert settings["track_space"] == 10.0

    assert mock_mqtt.publish.await_args.args == ("room/test/settings", json.dumps(settings))
    assert mock_mqtt.publish.await_args.kwargs == dict(retain=True)


@pytest.mark.asyncio
async def test_queue_settings_change_invalid(api_queue: APIQueue, mock_mqtt):
    settings = await api_queue.settings
    assert settings["validation_event_end_datetime"] is None

    mock_mqtt.publish.assert_not_awaited()
    api_queue.session_id = "admin"
    response = await api_queue.settings_put(
        payload={"validation_event_end_datetime": "Some nonsense that is not a datetime"}
    )
    assert response.status == 400
    mock_mqtt.publish.assert_not_awaited()


@pytest.mark.parametrize(
    "settings_fieldname",
    (
        "track_space",
        "validation_event_end_datetime",
        "preview_volume",
        "coming_soon_track_count",
        "validation_performer_names",
        "auto_reorder_queue",
    ),
)
async def test_queue_settings_validation_invalid(api_queue: APIQueue, settings_fieldname: str):
    api_queue.session_id = "admin"
    response = await api_queue.settings_put(payload={settings_fieldname: "NOT VALID"})
    assert response.status == 400
    error = response.json["context"][0]
    assert error["input"] == "NOT VALID"
    assert error["loc"][0] == settings_fieldname


@pytest.mark.asyncio
async def test_queue_add(api_queue: APIQueue, mock_mqtt):
    # queue is empty
    assert len(await api_queue.queue) == 0

    # reject add tracks that are not in track list
    response = await api_queue.post()
    assert response.status == 400
    response = await api_queue.post(track_id="NotRealTrackId", performer_name="test")
    assert response.status == 400

    mock_mqtt.publish.assert_not_awaited()
    # add track
    response = await api_queue.post(track_id="KAT_TUN_Your_side_Instrumental", performer_name="test")
    assert response.status == 200
    mock_mqtt.publish.assert_awaited_once()
    # check track now in queue
    queue = await api_queue.queue
    assert len(queue) == 1
    assert {"track_id": "KAT_TUN_Your_side_Instrumental", "performer_name": "test"}.items() <= queue[0].items()
    assert mock_mqtt.publish.await_args.args == ("room/test/queue", json.dumps(queue))
    assert mock_mqtt.publish.await_args.kwargs == dict(retain=True)


@pytest.mark.asyncio
async def test_queue_add_csv(api_queue: APIQueue):
    await api_queue.post(track_id="KAT_TUN_Your_side_Instrumental", performer_name="test1")
    csv = await api_queue.queue_csv
    assert csv.count(",") > 10  # TODO: assert this is valid csv?
    assert "test1" in csv


@pytest.mark.asyncio
async def test_queue_delete(api_queue: APIQueue, mock_mqtt):
    # populate queue
    assert len(await api_queue.queue) == 0
    await api_queue.post(track_id="KAT_TUN_Your_side_Instrumental", performer_name="test1")
    await api_queue.post(track_id="Animaniacs_OP", performer_name="test2")
    queue = await api_queue.queue
    assert len(queue) == 2

    # try to delete invalid
    mock_mqtt.publish.reset_mock()
    response = await api_queue.delete(queue_item_id=999)
    assert response.status == 404
    mock_mqtt.publish.assert_not_awaited()

    # delete
    response = await api_queue.delete(queue_item_id=queue[0]["id"])
    assert response.status == 200
    mock_mqtt.publish.assert_awaited_once()
    queue = await api_queue.queue
    assert len(queue) == 1
    assert queue[0]["track_id"] == "Animaniacs_OP"

    # session_id owner reject
    api_queue.session_id = "not_real"
    response = await api_queue.delete(queue_item_id=queue[0]["id"])
    assert response.status == 403

    # session_id admin can delete
    api_queue.session_id = "admin"
    response = await api_queue.delete(queue_item_id=queue[0]["id"])
    assert response.status == 200
    queue = await api_queue.queue
    assert len(queue) == 0


@pytest.mark.asyncio
async def test_queue_move(api_queue: APIQueue, mock_mqtt):
    # populate queue
    await api_queue.post(track_id="KAT_TUN_Your_side_Instrumental", performer_name="test1")
    await api_queue.post(track_id="Animaniacs_OP", performer_name="test2")
    await api_queue.post(track_id="Macross_Dynamite7_OP_Dynamite_Explosion", performer_name="test3")
    queue = await api_queue.queue
    assert len(queue) == 3

    # invalid moves
    mock_mqtt.publish.reset_mock()
    response = await api_queue.put()
    assert response.status == 400
    response = await api_queue.put(source=0, target=0)
    assert response.status == 403
    api_queue.session_id = "admin"
    response = await api_queue.put(source=0, target=0)
    assert response.status == 400
    mock_mqtt.publish.assert_not_awaited()

    # move
    response = await api_queue.put(source=queue[0]["id"], target=queue[2]["id"])
    assert response.status == 201
    mock_mqtt.publish.assert_awaited_once()
    queue = await api_queue.queue
    assert [i["track_id"] for i in queue] == [
        "Animaniacs_OP",
        "KAT_TUN_Your_side_Instrumental",
        "Macross_Dynamite7_OP_Dynamite_Explosion",
    ]
    # move to end
    response = await api_queue.put(source=queue[0]["id"], target=-1)
    queue = await api_queue.queue
    assert [i["track_id"] for i in queue] == [
        "KAT_TUN_Your_side_Instrumental",
        "Macross_Dynamite7_OP_Dynamite_Explosion",
        "Animaniacs_OP",
    ]


@pytest.mark.asyncio
async def test_queue_command(api_queue: APIQueue, mock_mqtt):
    # populate tracks
    await api_queue.post(track_id="KAT_TUN_Your_side_Instrumental", performer_name="test1")
    await api_queue.post(track_id="Animaniacs_OP", performer_name="test2")
    await api_queue.post(track_id="Macross_Dynamite7_OP_Dynamite_Explosion", performer_name="test3")
    queue = await api_queue.queue
    assert not any(queue_item["start_time"] for queue_item in queue), "no tracks should have a start time"

    # invalid commands
    mock_mqtt.publish.reset_mock()
    response = await api_queue.command("play")
    assert response.status == 403
    api_queue.session_id = "admin"
    response = await api_queue.command("not_real_command")
    assert response.status == 404
    mock_mqtt.publish.assert_not_awaited()

    # play
    response = await api_queue.command("play")
    assert response.status == 200
    mock_mqtt.publish.assert_awaited_once()

    queue = await api_queue.queue
    assert all(queue_item["start_time"] for queue_item in queue), "all tracks should have a start time"

    # stop
    response = await api_queue.command("stop")
    assert response.status == 200
    queue = await api_queue.queue
    assert not any(queue_item["start_time"] for queue_item in queue), "no tracks should have a start time"


@pytest.mark.asyncio
async def test_queue_updated_actions(api_queue: APIQueue):
    _original_session_id = api_queue.session_id
    api_queue.session_id = "admin"
    response = await api_queue.settings_put(payload={"validation_performer_names": ["valid_name1", "valid_name2"]})
    assert response.status == 200
    api_queue.session_id = _original_session_id

    settings = await api_queue.settings
    assert settings["validation_performer_names"] == ["valid_name1", "valid_name2"]

    response = await api_queue.post(track_id="KAT_TUN_Your_side_Instrumental", performer_name="invalid_name")
    assert response.status == 400
    assert "invalid_name" in str(response.json["context"])


@pytest.mark.asyncio
async def test_queue_updated_actions__end_datetime(api_queue: APIQueue):
    _original_session_id = api_queue.session_id
    api_queue.session_id = "admin"
    # set end_datetime to be now as bst and add a 10 mins so the track can be queued (if the event ends at this current millisecond, no tracks can be added)
    end_datetime = (
        datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=1), name="bst"))
        + datetime.timedelta(minutes=10)
    ).isoformat()
    response = await api_queue.settings_put(
        payload={
            "validation_event_end_datetime": end_datetime,
        }
    )
    assert response.status == 200
    api_queue.session_id = _original_session_id

    response = await api_queue.post(track_id="KAT_TUN_Your_side_Instrumental", performer_name="test_name")
    assert response.status == 200
