from datetime import datetime
import contextlib
from textwrap import dedent
from pathlib import Path
import uuid
from types import MappingProxyType
import typing as t

import ujson as json
import sanic
from sanic_ext import openapi
from sanic_ext.extensions.http.cors import add_cors
from sanic.log import logger as log
import pydantic


app = sanic.Sanic("karakara_queue")
app.config.update({
    k: v
    for k, v in {
        #'REDIS': "redis://redis:6379/0",
        #'MQTT': 'mqtt',  #:1883
        'PATH_TRACKS': 'tracks.json',
        'PATH_QUEUE': '_data',
    }.items()
    if k not in app.config.keys()
})
app.ext.openapi.describe(
    "KaraKara Queue API",
    version="0.0.0",
    description=dedent("""
    """),  # TODO: Markdown
)

app.config.FALLBACK_ERROR_FORMAT = "json"

# Allow dev-mode clients to connect to prod server.
# When allowing connections with credentials, allowed
# headers MUST be explicitly listed.
app.config.CORS_SUPPORTS_CREDENTIALS = True
app.config.CORS_ALLOW_HEADERS = ["Content-Type"]
app.config.CORS_ORIGINS = [
    "http://127.0.0.1:1234",  # browser2
    "http://127.0.0.1:1235",  # player2
    "http://127.0.0.1:1236",  # browser3
    "http://127.0.0.1:1237",  # player3
]
add_cors(app)


# Model ------------------------------------------------------------------------

from .queue_model import Queue, QueueItem
from .queue_validation import validate_queue, QueueValidationError


# Startup ----------------------------------------------------------------------

from .track_manager import TrackManager
@app.listener('before_server_start')
async def tracks_load(_app: sanic.Sanic, _loop):
    _app.ctx.track_manager = TrackManager(Path(str(_app.config.get('PATH_TRACKS'))))


from .settings_manager import SettingsManager, QueueSettings
from .queue_manager import QueueManagerCSVAsync
@app.listener('before_server_start')
async def queue_manager(_app: sanic.Sanic, _loop):
    path_queue = Path(str(_app.config.get('PATH_QUEUE')))
    log.info(f"[queue_manager] - {path_queue=}")
    _app.ctx.settings_manager = SettingsManager(path=path_queue)
    _app.ctx.queue_manager = QueueManagerCSVAsync(path=path_queue, settings=_app.ctx.settings_manager)


@app.listener('before_server_start')
async def aio_mqtt_configure(_app: sanic.Sanic, _loop):
    mqtt = _app.config.get('MQTT')
    if isinstance(mqtt, str):
        log.info("[mqtt] connecting")
        import aiomqtt
        _app.ctx.mqtt = aiomqtt.Client(mqtt)
        await _app.ctx.mqtt.__aenter__()
    elif mqtt:  # normally pass-through for mock mqtt object
        log.info("[mqtt] bypassed")
        _app.ctx.mqtt = mqtt
@app.listener('after_server_stop')
async def aio_mqtt_close(_app, _loop):
    mqtt = _app.config.get('MQTT')
    if isinstance(mqtt, str):
        log.info("[mqtt] closing")
        await _app.ctx.mqtt.__aexit__(None, None, None)



# Middleware -------------------------------------------------------------------

# pytest debugging - This is needed to see exceptions on failed tests. DEBUG=True wont give me json exceptions. SO CLUMSY!
# https://sanic.dev/en/guide/best-practices/exceptions.html#custom-error-handling
def exception_to_dict(exception: Exception) -> dict[str, str|int]:
    import traceback
    return {
        'status': 500,
        'message': 'Internal Server Error',
        'exception': "".join(traceback.TracebackException.from_exception(exception).format())
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



from .queue_manager import LoginManager, User
@app.on_request
async def attach_session_id_request(request: sanic.Request):
    request.ctx.session_id = request.cookies.get("session_id") or str(uuid.uuid4())
    request.ctx.user = LoginManager.from_session(request.ctx.session_id)
@app.on_response
async def attach_session_id(request: sanic.Request, response: sanic.HTTPResponse):
    if request.cookies.get("session_id") != request.ctx.session_id:
        response.cookies.add_cookie("session_id", request.ctx.session_id, secure=False, samesite=None)




@contextlib.asynccontextmanager
async def push_queue_to_mqtt(request, room_name):
    yield
    if hasattr(request.app.ctx, 'mqtt'):
        log.info(f"push_queue_to_mqtt {room_name}")
        await request.app.ctx.mqtt.publish(f"room/{room_name}/queue", json.dumps(request.app.ctx.queue_manager.for_json(room_name)), retain=True)

@contextlib.asynccontextmanager
async def push_settings_to_mqtt(request, room_name):
    yield
    if hasattr(request.app.ctx, 'mqtt'):
        log.info(f"push_settings_to_mqtt {room_name}")
        await request.app.ctx.mqtt.publish(f"room/{room_name}/settings", json.dumps(request.app.ctx.queue_manager.settings.get_json(room_name)), retain=True)


# Routes -----------------------------------------------------------------------

@app.get("/")
@openapi.definition(
    response=openapi.definitions.Response('redirect to openapi spec', status=302),
)
async def root(request):
    return sanic.response.redirect('/docs')


@app.get("/time.json")
@openapi.definition(
    response=openapi.definitions.Response({"application/json": float}),
)
async def time(request):
    return sanic.response.json(datetime.now().timestamp())


# Queue -----------------------------------------------------------------------

room_blueprint = sanic.blueprints.Blueprint('room', url_prefix='/room/<room_name:([A-Za-z0-9_-]{1,32})>')
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

class LoginRequest:
    password: str
@room_blueprint.post("/login.json")
@openapi.definition(
    body={"application/json": LoginRequest},
    response=[
        openapi.definitions.Response({"application/json": User}, status=200),
    ],
)
async def login(request, room_name):
    if not request.app.ctx.settings_manager.room_exists(room_name):
        if not request.json.get("create"):
            raise sanic.exceptions.NotFound(message=f"Room '{room_name}' not found")
        request.app.ctx.settings_manager.set_json(room_name, {})
    user = LoginManager.login(room_name, None, request.json["password"], request.ctx.session_id)
    request.ctx.session_id = user.session_id
    return sanic.response.json(user.__dict__)


# Queue / Tracks --------------------------------------------------------------

@room_blueprint.get("/tracks.json")
@openapi.definition(
    response=openapi.definitions.Response({"application/json": NullObjectJson}),
)
async def tracks(request, room_name):
    return await sanic.response.file(request.app.config.get('PATH_TRACKS'))


# Queue / Settings ------------------------------------------------------------

@room_blueprint.get("/settings.json")
@openapi.definition(
    response=openapi.definitions.Response({"application/json": QueueSettings}),
)
async def get_settings(request, room_name):
    return sanic.response.json(request.app.ctx.settings_manager.get_json(room_name))

@room_blueprint.put("/settings.json")
@openapi.definition(
    body={"application/json": QueueSettings},
    response=openapi.definitions.Response({"application/json": NullObjectJson}),
)
async def update_settings(request, room_name):
    if not request.ctx.user.is_admin:
        raise sanic.exceptions.Forbidden(message="Only admins can update settings")
    async with push_settings_to_mqtt(request, room_name):
        try:
            request.app.ctx.settings_manager.set_json(room_name, request.json)
            log.info(f"Updated settings for {room_name} with {request.json}")
        except pydantic.ValidationError as ex:
            log.warning(f"Rejected settings for {room_name} with {request.json}")
            raise sanic.exceptions.InvalidUsage(message="invalid settings", context=json.loads(ex.json()))
        return sanic.response.json({})


# Queue / Queue ---------------------------------------------------------------

@room_blueprint.get("/queue.csv")
@openapi.definition(
    response=[
        openapi.definitions.Response({"text/csv": str}),
        openapi.definitions.Response('queue not found', status=400),
    ]
)
async def queue_csv(request, room_name):
    path_csv = request.app.ctx.queue_manager.path_csv(room_name)
    if not path_csv.is_file():
        raise sanic.exceptions.NotFound()
    return await sanic.response.file(path_csv)

@room_blueprint.get("/queue.json")
@openapi.definition(
    response=openapi.definitions.Response({"application/json": [QueueItemJson]}),
)
async def queue_json(request, room_name):
    return sanic.response.json(request.app.ctx.queue_manager.for_json(room_name))


class QueueItemAdd:
    track_id: str
    performer_name: str
@room_blueprint.post("/queue.json")
@openapi.definition(
    body={"application/json": QueueItemAdd},
    response=[
        openapi.definitions.Response({"application/json": QueueItemJson}, status=200),
        openapi.definitions.Response('missing fields', status=400),
        openapi.definitions.Response('track_id invalid', status=400),
    ],
)
async def add_queue_item(request, room_name):
    tracks = request.app.ctx.track_manager.tracks  # Performance note: This fetches the mtime of the tracks file each time
    # Validation
    if not request.json or frozenset(request.json.keys()) != frozenset(('track_id', 'performer_name')):
        raise sanic.exceptions.InvalidUsage(message="missing fields", context=request.json)
    track_id = request.json['track_id']
    if track_id not in tracks:
        raise sanic.exceptions.InvalidUsage(message="track_id invalid", context=track_id)
    performer_name = request.json['performer_name']
    # Queue update
    async with push_queue_to_mqtt(request, room_name):
        async with request.app.ctx.queue_manager.async_queue_modify_context(room_name) as queue:
            queue_item = QueueItem(
                track_id=track_id,
                track_duration=tracks[track_id]["duration"],
                session_id=request.ctx.session_id,
                performer_name=performer_name,
            )
            queue.add(queue_item)
            # Post process queue state - functions are configurable per queue
            if not request.ctx.user.is_admin:
                try:
                    validate_queue(queue)
                except QueueValidationError as ex:
                    log.info(f"add failed {ex=}")
                    # NOTE: the client has special behaviour for the specific
                    # hard-coded string "queue validation failed". In the long
                    # term we should add a more structured error format, but
                    # for now, we require this exact string.
                    raise sanic.exceptions.InvalidUsage(message="queue validation failed", context=str(ex))
                    # TODO: validation error properly!
            return sanic.response.json(queue_item.asdict())


@room_blueprint.delete(r"/queue/<queue_item_id:(\d+).json>")
@openapi.definition(
    response=openapi.definitions.Response({"application/json": QueueItemJson}),
)
async def delete_queue_item(request, room_name, queue_item_id):
    queue_item_id = int(queue_item_id)
    async with push_queue_to_mqtt(request, room_name):
        async with request.app.ctx.queue_manager.async_queue_modify_context(room_name) as queue:
            _, queue_item = queue.get(queue_item_id)
            if not queue_item:
                raise sanic.exceptions.NotFound()
            if queue_item.session_id != request.ctx.session_id and not request.ctx.user.is_admin:
                raise sanic.exceptions.Forbidden(message="queue_item.session_id does not match session_id")
            queue.delete(queue_item_id)
            return sanic.response.json(queue_item.asdict())


class QueueItemMove:
    source: int
    target: int
@room_blueprint.put("/queue.json")
@openapi.definition(
    body={"application/json": QueueItemMove},
    response=openapi.definitions.Response({"application/json": NullObjectJson}, description="...", status=201),
)
async def move_queue_item(request, room_name):
    try:
        source = int(request.json.get('source'))
        target = int(request.json.get('target'))
    except (ValueError, TypeError):
        raise sanic.exceptions.InvalidUsage(message="source and target args required", context=request.json)
    if not request.ctx.user.is_admin:
        raise sanic.exceptions.Forbidden(message="queue updates are for admin only")
    async with push_queue_to_mqtt(request, room_name):
        async with request.app.ctx.queue_manager.async_queue_modify_context(room_name) as queue:
            queue.move(source, target)
            return sanic.response.json({}, status=201)


# Queue / Commands ------------------------------------------------------------

class CommandReturn():
    is_playing: bool
@room_blueprint.get("/command/<command:([a-z_]+).json>")
@openapi.definition(
    response=[
        openapi.definitions.Response({"application/json": CommandReturn}, status=200),
        openapi.definitions.Response('invalid command', status=400),
        openapi.definitions.Response('admin required', status=403),
    ]
)
async def queue_command(request, room_name, command):
    if not request.ctx.user.is_admin:
        raise sanic.exceptions.Forbidden(message="commands are for admin only")
    if command not in {'play', 'stop', 'seek_forwards', 'seek_backwards', 'skip'}:
        raise sanic.exceptions.NotFound(message='invalid command')
    async with push_queue_to_mqtt(request, room_name):
        async with request.app.ctx.queue_manager.async_queue_modify_context(room_name) as queue:
            getattr(queue, command)()
            return sanic.response.json({'is_playing': bool(queue.is_playing)})


# end Queue --------------------------------------------------------------------


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, workers=4, dev=True, access_log=True, auto_reload=True)
