import pytest
import collections.abc
import datetime
import typing as t
import collections.abc as ct

from sanic.response import HTTPResponse
import ujson as json
from api_queue.api_types import App


class APIQueue:
    def __init__(self, app: App, queue: str):
        self.app = app
        self._queue = queue

    async def login(self) -> None:
        request, response = await self.app.asgi_client.post(
            f"/room/{self._queue}/login.json", data=json.dumps(dict(password=self._queue, create=True))
        )
        assert response.status == 200
        assert response.json["is_admin"] is True

    async def logout(self) -> None:
        request, response = await self.app.asgi_client.post(
            f"/room/{self._queue}/login.json", data=json.dumps(dict(password=""))
        )
        assert response.status == 200
        assert response.json["is_admin"] is False

    @property
    async def queue_csv(self) -> str:
        request, response = await self.app.asgi_client.get(f"/room/{self._queue}/queue.csv")
        return response.text

    @property
    async def queue(self) -> ct.Sequence[ct.Mapping[str, t.Any]]:
        request, response = await self.app.asgi_client.get(f"/room/{self._queue}/queue.json")
        return response.json

    @property
    async def tracks(self) -> ct.Mapping[str, ct.Mapping[str, t.Any]]:
        request, response = await self.app.asgi_client.get(f"/room/{self._queue}/tracks.json")
        return response.json

    @property
    async def settings(self) -> ct.Mapping[str, t.Any]:
        request, response = await self.app.asgi_client.get(f"/room/{self._queue}/settings.json")
        return response.json

    async def settings_put(self, payload: ct.Mapping[str, t.Any]) -> HTTPResponse:
        request, response = await self.app.asgi_client.put(
            f"/room/{self._queue}/settings.json", data=json.dumps(payload)
        )
        return response

    async def post(self, **kwargs) -> HTTPResponse:
        request, response = await self.app.asgi_client.post(f"/room/{self._queue}/queue.json", data=json.dumps(kwargs))
        return response

    async def delete(self, queue_item_id: int) -> HTTPResponse:
        request, response = await self.app.asgi_client.delete(f"/room/{self._queue}/queue/{queue_item_id}.json")
        return response

    async def put(self, **kwargs) -> HTTPResponse:
        request, response = await self.app.asgi_client.put(f"/room/{self._queue}/queue.json", data=json.dumps(kwargs))
        return response

    async def command(self, command: str) -> HTTPResponse:
        request, response = await self.app.asgi_client.get(f"/room/{self._queue}/command/{command}.json")
        return response


@pytest.fixture
async def api_queue(app: App):
    return APIQueue(app, "test")


@pytest.mark.asyncio
async def test_root(app: App):
    request, response = await app.asgi_client.get("/")
    assert response.status == 302


@pytest.mark.asyncio
async def test_queue_invalid_name(app: App):
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
    await api_queue.login()
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
    await api_queue.login()
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
    await api_queue.login()
    response = await api_queue.settings_put(payload={settings_fieldname: "NOT VALID"})
    assert response.status == 400


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
    # user can populate queue
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

    # user can delete own tracks
    response = await api_queue.delete(queue_item_id=queue[0]["id"])
    assert response.status == 200
    mock_mqtt.publish.assert_awaited_once()
    queue = await api_queue.queue
    assert len(queue) == 1
    assert queue[0]["track_id"] == "Animaniacs_OP"

    # user can't delete other people's tracks
    api_queue.app.asgi_client.cookies.delete("kksid")
    response = await api_queue.delete(queue_item_id=queue[0]["id"])
    assert response.status == 403

    # admin can delete other people's tracks
    await api_queue.login()
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
    await api_queue.login()
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
    await api_queue.login()
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
    await api_queue.login()
    response = await api_queue.settings_put(payload={"validation_performer_names": ["valid_name1", "valid_name2"]})
    assert response.status == 200
    await api_queue.logout()

    settings = await api_queue.settings
    assert settings["validation_performer_names"] == ["valid_name1", "valid_name2"]

    response = await api_queue.post(track_id="KAT_TUN_Your_side_Instrumental", performer_name="invalid_name")
    assert response.status == 400
    assert "invalid_name" in str(response.json["context"])


@pytest.mark.asyncio
async def test_queue_updated_actions__end_datetime(api_queue: APIQueue):
    await api_queue.login()
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
    await api_queue.logout()

    response = await api_queue.post(track_id="KAT_TUN_Your_side_Instrumental", performer_name="test_name")
    assert response.status == 200
