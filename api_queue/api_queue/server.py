import enum
import contextlib
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from textwrap import dedent
from collections.abc import AsyncGenerator

import aiomqtt
import pydantic
import sanic
import ujson as json
from sanic.log import logger as log
from sanic_ext import openapi, validate
import sanic.blueprints
import sanic.handlers
import sanic.response
import sanic.exceptions

from .queue_model import QueueItem
from .queue_updated_actions import QueueValidationError, queue_updated_actions
from .track_manager import TrackManager
from .queue_manager import QueueManager
from .settings_manager import QueueSettings, SettingsManager
from .login_manager import LoginManager, User
from .background_tasks import background_tracks_update_event
from .api_types import App, Request


app = App("karakara_queue")
app.config.update(
    {
        k: v
        for k, v in {
            "MQTT": None,
            "PATH_TRACKS": "tracks.json",
            "PATH_QUEUE": "_data",
            "BACKGROUND_TASK_TRACK_UPDATE_ENABLED": True,
        }.items()
        if k not in app.config.keys()
    }
)
app.ext.openapi.describe(
    "KaraKara Queue API",
    version="0.0.0",
)

app.config.FALLBACK_ERROR_FORMAT = "json"

# Startup ----------------------------------------------------------------------


@app.listener("before_server_start")
async def tracks_load(app: App, _loop):
    app.ctx.track_manager = TrackManager(Path(app.config.PATH_TRACKS))


@app.listener("before_server_start")
async def queue_manager(app: App, _loop):
    path_queue = Path(app.config.PATH_QUEUE)
    log.info(f"[queue_manager] - {path_queue=}")
    app.ctx.path_queue = path_queue
    app.ctx.login_manager = LoginManager(path=path_queue)
    app.ctx.settings_manager = SettingsManager(path=path_queue)
    app.ctx.queue_manager = QueueManager(path=path_queue, settings=app.ctx.settings_manager)


@app.listener("before_server_start")
async def aio_mqtt_configure(app: App, _loop):
    mqtt = app.config.MQTT
    if isinstance(mqtt, str):
        log.info("[mqtt] connecting")
        app.ctx.mqtt = aiomqtt.Client(mqtt)
        await app.ctx.mqtt.__aenter__()
    elif mqtt:  # normally pass-through for mock mqtt object
        log.info("[mqtt] bypassed")
        app.ctx.mqtt = mqtt


@app.listener("after_server_stop")
async def aio_mqtt_close(app: App, _loop):
    mqtt = app.config.MQTT
    if isinstance(mqtt, str):
        log.info("[mqtt] closing")
        await app.ctx.mqtt.__aexit__(None, None, None)


# Middleware -------------------------------------------------------------------


# pytest debugging - This is needed to see exceptions on failed tests. DEBUG=True wont give me json exceptions. SO CLUMSY!
# https://sanic.dev/en/guide/best-practices/exceptions.html#custom-error-handling
def exception_to_dict(exception: Exception) -> dict[str, str | int]:
    import traceback

    return {
        "status": 500,
        "message": "Internal Server Error",
        "exception": "".join(traceback.TracebackException.from_exception(exception).format()),
    }


class CustomErrorHandler(sanic.handlers.ErrorHandler):
    def default(self, request, exception):
        if isinstance(exception, sanic.exceptions.SanicException):
            return super().default(request, exception)
        if isinstance(exception, AssertionError):
            return super().default(request, sanic.exceptions.InvalidUsage(*exception.args))
        log.exception("Error:")
        return sanic.response.json(exception_to_dict(exception), status=500)


app.error_handler = CustomErrorHandler()


@app.on_request
async def attach_session_id_request(request: Request):
    request.ctx.session_id = request.cookies.get("kksid")


@contextlib.asynccontextmanager
async def push_queue_to_mqtt(app: App, room_name: str) -> AsyncGenerator[None]:
    yield
    if hasattr(app.ctx, "mqtt"):
        log.info(f"push_queue_to_mqtt {room_name}")
        await app.ctx.mqtt.publish(
            f"room/{room_name}/queue",
            json.dumps(app.ctx.queue_manager.for_json(room_name)),
            retain=True,
        )


@contextlib.asynccontextmanager
async def push_settings_to_mqtt(app: App, room_name: str) -> AsyncGenerator[None]:
    yield
    if hasattr(app.ctx, "mqtt"):
        log.info(f"push_settings_to_mqtt {room_name}")
        await app.ctx.mqtt.publish(
            f"room/{room_name}/settings",
            app.ctx.queue_manager.settings.get(room_name).model_dump_json(),
            retain=True,
        )


# Routes -----------------------------------------------------------------------


@app.get("/")
@openapi.definition(
    response=openapi.definitions.Response("redirect to openapi spec", status=302),
)
async def root(request: Request):
    return sanic.response.redirect("/api/docs")


@app.get("/time.json")
@openapi.definition(
    response=openapi.definitions.Response({"application/json": float}),
)
async def time(request: Request):
    return sanic.response.json(datetime.now().timestamp())


@app.post("/analytics.json")
@openapi.definition(
    response=openapi.definitions.Response({"application/json": bool}),
)
async def analytics(request: Request):
    try:
        with open("/logs/analytics.json", "a", encoding="utf8") as f:
            data = request.json
            data["remote_addr"] = request.remote_addr
            data["time"] = datetime.now().isoformat()
            data["user_agent"] = request.headers.get("user-agent")
            data["session"] = request.ctx.session_id
            f.write(json.dumps(data) + "\n")
        return sanic.response.json(True)
    except Exception as e:
        log.exception("analytics.json error")
        return sanic.response.json(False)


# Queue -----------------------------------------------------------------------

room_blueprint = sanic.blueprints.Blueprint("room", url_prefix="/room/<room_name:([A-Za-z0-9_-]{1,32})>")
app.blueprint(room_blueprint)


class NullObjectJson:
    pass


class QueueItemJson:
    # We cant use QueueItem(dataclass) directly as the types are not the same as it's `.to_dict()`
    track_id: str
    track_duration: float
    session_id: str
    performer_name: str
    start_time: float
    id: int


# Queue / Login ---------------------------------------------------------------


class LoginRequest(pydantic.BaseModel):
    create: bool = False
    password: str


@room_blueprint.post("/login.json")
@validate(json=LoginRequest)
@openapi.definition(
    body={"application/json": LoginRequest},
    response=[
        openapi.definitions.Response({"application/json": User}, status=200),
    ],
)
async def login(request: Request, room_name: str, body: LoginRequest):
    if not request.app.ctx.settings_manager.room_exists(room_name):
        if not body.create:
            raise sanic.exceptions.NotFound(message=f"Room '{room_name}' not found")
        request.app.ctx.settings_manager.set(room_name, QueueSettings())

    if not request.ctx.session_id:
        request.ctx.session_id = str(uuid.uuid4())
    user = request.app.ctx.login_manager.login(room_name, request.ctx.session_id, body.password)
    resp = sanic.response.json(user.model_dump(mode="json"))
    next_year = datetime.now() + timedelta(days=400)
    resp.cookies.add_cookie("kksid", request.ctx.session_id, samesite="strict", expires=next_year)
    return resp


# Queue / Tracks --------------------------------------------------------------


@room_blueprint.get("/tracks.json")
@openapi.definition(
    response=openapi.definitions.Response({"application/json": NullObjectJson}),
    description=dedent(
        """
        Dev convenience.
        Not used by production clients.
        Nginx serves this static content.
    """
    ),
)
async def tracks(request: Request, room_name: str):
    filename: str = request.app.config.PATH_TRACKS
    return await sanic.response.file(filename)


# Queue / Settings ------------------------------------------------------------


@room_blueprint.get("/settings.json")
@openapi.definition(
    response=openapi.definitions.Response({"application/json": QueueSettings}),
    description=dedent(
        """
        Dev convenience.
        Not used by production clients.
        settings received by mqtt event
    """
    ),
)
async def get_settings(request: Request, room_name: str):
    return sanic.response.raw(
        request.app.ctx.settings_manager.get(room_name).model_dump_json(),
        headers={"content-type": "application/json"},
    )


@room_blueprint.put("/settings.json")
@validate(json=QueueSettings)
@openapi.definition(
    body={"application/json": QueueSettings},
    response=openapi.definitions.Response({"application/json": NullObjectJson}),
)
async def update_settings(request: Request, room_name: str, body: QueueSettings):
    user = request.app.ctx.login_manager.load(room_name, request.ctx.session_id)
    if not user.is_admin:
        raise sanic.exceptions.Forbidden(message="Only admins can update settings")
    async with push_settings_to_mqtt(request.app, room_name):
        request.app.ctx.settings_manager.set(room_name, body)
        log.info(f"Updated settings for {room_name} with {request.json}")
        return sanic.response.json({})


# Queue / Queue ---------------------------------------------------------------


@room_blueprint.get("/queue.csv")
@openapi.definition(
    response=[
        openapi.definitions.Response({"text/csv": str}),
        openapi.definitions.Response("queue not found", status=400),
    ],
    description=dedent(
        """
        Dev convenience.
        Not used by production clients.
        queue received by mqtt event.
        Useful for debugging to see raw datastore on disk.
    """
    ),
)
async def queue_csv(request: Request, room_name: str):
    path_csv = request.app.ctx.queue_manager.path_csv(room_name)
    if not path_csv.is_file():
        raise sanic.exceptions.NotFound()
    return await sanic.response.file(path_csv)


@room_blueprint.get("/queue.json")
@openapi.definition(
    response=openapi.definitions.Response({"application/json": [QueueItemJson]}),
    description=dedent(
        """
        Dev convenience.
        Not used by production clients.
        queue received by mqtt event
    """
    ),
)
async def queue_json(request: Request, room_name: str):
    return sanic.response.json(request.app.ctx.queue_manager.for_json(room_name))


class QueueItemAdd(pydantic.BaseModel):
    track_id: str
    performer_name: str
    video_variant: str | None = None
    subtitle_variant: str | None = None


@room_blueprint.post("/queue.json")
@validate(json=QueueItemAdd)
@openapi.definition(
    body={"application/json": QueueItemAdd},
    response=[
        openapi.definitions.Response({"application/json": QueueItemJson}, status=200),
        openapi.definitions.Response("missing fields", status=400),
        openapi.definitions.Response("track_id invalid", status=400),
    ],
)
async def add_queue_item(request: Request, room_name: str, body: QueueItemAdd):
    user = request.app.ctx.login_manager.load(room_name, request.ctx.session_id)
    track_durations = request.app.ctx.track_manager.track_durations
    # Validation
    if request.ctx.session_id is None:
        raise sanic.exceptions.InvalidUsage(message="session_id missing")
    if body.track_id not in track_durations:
        raise sanic.exceptions.InvalidUsage(message="track_id invalid", context={"track_id": body.track_id})
    if body.performer_name.strip() == "":
        raise sanic.exceptions.InvalidUsage(message="Performer name cannot be empty")
    # Queue update
    async with push_queue_to_mqtt(request.app, room_name):
        async with request.app.ctx.queue_manager.async_queue_modify_context(room_name) as queue:
            queue_item = QueueItem(
                track_id=body.track_id,
                track_duration=track_durations[body.track_id],
                session_id=request.ctx.session_id,
                performer_name=body.performer_name,
                video_variant=body.video_variant,
                subtitle_variant=body.subtitle_variant,
            )
            queue.add(queue_item)

            if not user.is_admin:
                try:
                    queue_updated_actions(queue)
                except QueueValidationError as ex:
                    log.info(f"add failed {ex=}")
                    # NOTE: the client has special behavior for the specific
                    # hard-coded string "queue validation failed". In the long
                    # term we should add a more structured error format, but
                    # for now, we require this exact string.
                    raise sanic.exceptions.InvalidUsage(message="queue validation failed", context={"exc": str(ex)})
                    # TODO: validation error properly!
            return sanic.response.json(queue_item.model_dump(mode="json"))


@room_blueprint.delete(r"/queue/<queue_item_id_str:(\d+).json>")
@openapi.definition(
    response=openapi.definitions.Response({"application/json": QueueItemJson}),
)
async def delete_queue_item(request: Request, room_name: str, queue_item_id_str: str):
    user = request.app.ctx.login_manager.load(room_name, request.ctx.session_id)
    queue_item_id = int(queue_item_id_str)
    async with push_queue_to_mqtt(request.app, room_name):
        async with request.app.ctx.queue_manager.async_queue_modify_context(room_name) as queue:
            _, queue_item = queue.get(queue_item_id)
            if not queue_item:
                raise sanic.exceptions.NotFound()
            if queue_item.session_id != request.ctx.session_id and not user.is_admin:
                raise sanic.exceptions.Forbidden(message="queue_item.session_id does not match session_id")
            queue.delete(queue_item_id)
            return sanic.response.json(queue_item.model_dump(mode="json"))


class QueueItemMove(pydantic.BaseModel):
    source: int
    target: int


@room_blueprint.put("/queue.json")
@validate(json=QueueItemMove)
@openapi.definition(
    body={"application/json": QueueItemMove},
    response=openapi.definitions.Response({"application/json": NullObjectJson}, description="...", status=201),
)
async def move_queue_item(request: Request, room_name: str, body: QueueItemMove):
    user = request.app.ctx.login_manager.load(room_name, request.ctx.session_id)
    if not user.is_admin:
        raise sanic.exceptions.Forbidden(message="queue updates are for admin only")
    async with push_queue_to_mqtt(request.app, room_name):
        async with request.app.ctx.queue_manager.async_queue_modify_context(room_name) as queue:
            queue.move(body.source, body.target)
            return sanic.response.json({}, status=201)


# Queue / Commands ------------------------------------------------------------


class Commands(enum.StrEnum):
    PLAY = enum.auto()
    PLAY_ONE = enum.auto()
    STOP = enum.auto()
    SEEK_FORWARDS = enum.auto()
    SEEK_BACKWARDS = enum.auto()
    SKIP = enum.auto()


class CommandReturn:
    is_playing: bool


@room_blueprint.get("/command/<command:([a-z_]+).json>")
@openapi.definition(
    description=dedent(
        f"""
        Valid commands {', '.join(map(str, Commands))}
    """
    ),
    response=[
        openapi.definitions.Response({"application/json": CommandReturn}, status=200),
        openapi.definitions.Response("invalid command", status=400),
        openapi.definitions.Response("admin required", status=403),
    ],
)
async def queue_command(request: Request, room_name: str, command: str):
    user = request.app.ctx.login_manager.load(room_name, request.ctx.session_id)
    if not user.is_admin:
        raise sanic.exceptions.Forbidden(message="commands are for admin only")
    if command not in Commands:
        raise sanic.exceptions.NotFound(message="invalid command")
    async with push_queue_to_mqtt(request.app, room_name):
        async with request.app.ctx.queue_manager.async_queue_modify_context(room_name) as queue:
            getattr(queue, command)()
            return sanic.response.json({"is_playing": bool(queue.is_playing)})


# Background Tasks -------------------------------------------------------------

app.add_task(background_tracks_update_event(app))


# Main -------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, dev=True, access_log=True, auto_reload=True)
