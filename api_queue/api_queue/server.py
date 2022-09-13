import random
import contextlib
from textwrap import dedent
from pathlib import Path

try:
    import ujson as json
except ImportError:
    import json

import sanic
from sanic_ext import openapi
from sanic.log import logger as log

from ._utils import harden



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


# Startup ----------------------------------------------------------------------

@app.listener('before_server_start')
async def tracks_load(_app: sanic.Sanic, _loop):
    path_tracks = Path(_app.config.get('PATH_TRACKS'))
    log.info(f"[tracks] loading - {path_tracks=}")
    if path_tracks.is_file():
        with path_tracks.open() as filehandle:
            _app.ctx.tracks = harden(json.load(filehandle))
    else:
        log.error('No tracks.json file present or provided. api_queue WILL NOT FUNCTION IN PRODUCTION. processmedia2 should output this file when encoding is complete')
        _app.ctx.tracks = {}


from .queue import QueueManagerCSVAsync, QueueItem, SettingsManager
@app.listener('before_server_start')
async def queue_manager(_app: sanic.Sanic, _loop):
    path_queue = _app.config.get('PATH_QUEUE')
    log.info(f"[queue_manager] - {path_queue=}")
    _app.ctx.settings_manager = SettingsManager(path=path_queue)
    _app.ctx.queue_manager = QueueManagerCSVAsync(path=path_queue, settings=_app.ctx.settings_manager)


@app.listener('before_server_start')
async def aio_mqtt_configure(_app: sanic.Sanic, _loop):
    mqtt = _app.config.get('MQTT')
    if isinstance(mqtt, str):
        log.info("[mqtt] connecting")
        from asyncio_mqtt import Client as MqttClient, MqttError
        _app.ctx.mqtt = MqttClient(mqtt)
        await _app.ctx.mqtt.connect()
    elif mqtt:  # normally pass-through for mock mqtt object
        log.info("[mqtt] bypassed")
        _app.ctx.mqtt = mqtt
@app.listener('after_server_stop')
async def aio_mqtt_close(_app, _loop):
    mqtt = _app.config.get('MQTT')
    if isinstance(mqtt, str):
        log.info("[mqtt] closing")
        await _app.ctx.mqtt.disconnect()



# Middleware -------------------------------------------------------------------

# pytest debugging - This is needed to see exceptions on failed tests. DEBUG=True wont give me json exceptions. SO CLUMSY!
# https://sanic.dev/en/guide/best-practices/exceptions.html#custom-error-handling
class CustomErrorHandler(sanic.handlers.ErrorHandler):
    def default(self, request, exception):
        if isinstance(exception, sanic.exceptions.SanicException):
            return super().default(request, exception)
        if isinstance(exception, AssertionError):
            return super().default(request, sanic.exceptions.InvalidUsage(*exception.args))
        log.exception("Error:")
        import traceback
        return sanic.response.json({'exception': "".join(traceback.TracebackException.from_exception(exception).format())}, status=500)
app.error_handler = CustomErrorHandler()



@app.middleware("request")
async def attach_session_id_request(request):
    request.ctx.session_id = request.cookies.get("session_id") or str(random.random())
    request.ctx.is_admin = request.ctx.session_id == "admin"
@app.middleware("response")
async def attach_session_id(request, response):
    if request.cookies.get("session_id") != request.ctx.session_id:
        response.cookies["session_id"] = request.ctx.session_id




@contextlib.asynccontextmanager
async def push_queue_to_mqtt(request, queue_id):
    yield
    if hasattr(request.app.ctx, 'mqtt'):
        log.info(f"push_queue_to_mqtt {queue_id}")
        await request.app.ctx.mqtt.publish(f"room/{queue_id}/queue", json.dumps(request.app.ctx.queue_manager.for_json(queue_id)), retain=True)

@contextlib.asynccontextmanager
async def push_settings_to_mqtt(request, queue_id):
    yield
    if hasattr(request.app.ctx, 'mqtt'):
        log.info(f"push_settings_to_mqtt {queue_id}")
        await request.app.ctx.mqtt.publish(f"room/{queue_id}/settings", json.dumps(request.app.ctx.queue_manager.settings.get_json(queue_id)), retain=True)


# Routes -----------------------------------------------------------------------



@app.get("/")
@openapi.definition(
    response=openapi.definitions.Response('redirect to openapi spec', status=302),
)
async def root(request):
    return sanic.response.redirect('/docs')


# Queue ------------------------------------------------------------------------

queue_blueprint = sanic.blueprints.Blueprint('queue', url_prefix='/queue')
app.blueprint(queue_blueprint)


class NullObjectJson:
    pass
class QueueItemJson:
    track_id: str
    track_duration: float
    session_id: str
    performer_name: str
    start_time: float
    id: int



from .queue import LoginManager, User
class LoginRequest:
    password: str
@queue_blueprint.post("/<queue_id:str>/login.json")
@openapi.definition(
    body={"application/json": LoginRequest},
    response=[
        openapi.definitions.Response({"application/json": User}, status=200),
    ],
)
async def login(request, queue_id):
    user = LoginManager.login(queue_id, None, request.json["password"])
    if user.is_admin:
        request.ctx.session_id = "admin"
    else:
        request.ctx.session_id = str(random.random())
    return sanic.response.json(user.__dict__)


@queue_blueprint.get("/<queue_id:str>/tracks.json")
@openapi.definition(
    response=openapi.definitions.Response({"application/json": NullObjectJson}),
)
async def tracks(request, queue_id):
    return await sanic.response.file(request.app.config.get('PATH_TRACKS'))


@queue_blueprint.get("/<queue_id:str>/queue.csv")
@openapi.definition(
    response=openapi.definitions.Response({"text/csv": str}),
)
async def queue_csv(request, queue_id):
    return await sanic.response.file(request.app.ctx.queue_manager.path_csv(queue_id))

@queue_blueprint.get("/<queue_id:str>/queue.json")
@openapi.definition(
    response=openapi.definitions.Response({"application/json": [QueueItemJson]}),
)
async def queue_json(request, queue_id):
    return sanic.response.json(request.app.ctx.queue_manager.for_json(queue_id))

@queue_blueprint.get("/<queue_id:str>/settings.json")
@openapi.definition(
    response=openapi.definitions.Response({"application/json": NullObjectJson}),
)
async def get_settings(request, queue_id):
    return sanic.response.json(request.app.ctx.settings_manager.get_json(queue_id))

@queue_blueprint.put("/<queue_id:str>/settings.json")
@openapi.definition(
    body={"application/json": {}},
    response=openapi.definitions.Response({"application/json": NullObjectJson}),
)
async def update_settings(request, queue_id):
    if not request.ctx.is_admin:
        raise sanic.exceptions.Forbidden(message="Only admins can update settings")
    async with push_settings_to_mqtt(request, queue_id):
        log.info(f"Updating settings for {queue_id} to {request.json}")
        request.app.ctx.settings_manager.set_json(queue_id, request.json)
        return sanic.response.json({})



class QueueItemAdd:
    track_id: str
    performer_name: str
@queue_blueprint.post("/<queue_id:str>/queue.json")
@openapi.definition(
    body={"application/json": QueueItemAdd},
    response=[
        openapi.definitions.Response({"application/json": QueueItemJson}, status=200),
        openapi.definitions.Response('missing fields', status=400),
        openapi.definitions.Response('track_id invalid', status=400),
    ],
)
async def add_queue_item(request, queue_id):
    # Validation
    if not request.json or frozenset(request.json.keys()) != frozenset(('track_id', 'performer_name')):
        raise sanic.exceptions.InvalidUsage(message="missing fields", context=request.json)
    track_id = request.json['track_id']
    if track_id not in request.app.ctx.tracks:
        raise sanic.exceptions.InvalidUsage(message="track_id invalid", context=track_id)
    performer_name = request.json['performer_name']
    # TODO:
    #   Check performer name in performer name list?
    #   Check event start
    # Queue update
    async with push_queue_to_mqtt(request, queue_id):
        async with request.app.ctx.queue_manager.async_queue_modify_context(queue_id) as queue:
            # TODO:
            #   Check duplicate performer
            #   Check duplicate tracks
            #   Check event end
            #   Check queue limit (priority token?)
            queue_item = QueueItem(
                track_id=track_id,
                track_duration=request.app.ctx.tracks[track_id]["duration"],
                session_id=request.ctx.session_id,
                performer_name=performer_name,
            )
            queue.add(queue_item)
            return sanic.response.json(queue_item.asdict())


@queue_blueprint.delete(r"/<queue_id:str>/queue/<queue_item_id:(\d+).json>")
@openapi.definition(
    response=openapi.definitions.Response({"application/json": QueueItemJson}),
)
async def delete_queue_item(request, queue_id, queue_item_id):
    queue_item_id = int(queue_item_id)
    async with push_queue_to_mqtt(request, queue_id):
        async with request.app.ctx.queue_manager.async_queue_modify_context(queue_id) as queue:
            _, queue_item = queue.get(queue_item_id)
            if not queue_item:
                raise sanic.exceptions.NotFound()
            if queue_item.session_id != request.ctx.session_id and not request.ctx.is_admin:
                raise sanic.exceptions.Forbidden(message="queue_item.session_id does not match session_id")
            queue.delete(queue_item_id)
            return sanic.response.json(queue_item.asdict())


class QueueItemMove:
    source: int
    target: int
@queue_blueprint.put("/<queue_id:str>/queue.json")
@openapi.definition(
    body={"application/json": QueueItemMove},
    response=openapi.definitions.Response({"application/json": NullObjectJson}, description="...", status=201),
)
async def move_queue_item(request, queue_id):
    try:
        source = int(request.json.get('source'))
        target = int(request.json.get('target'))
    except (ValueError, TypeError):
        raise sanic.exceptions.InvalidUsage(message="source and target args required", context=request.json)
    if not request.ctx.is_admin:
        raise sanic.exceptions.Forbidden(message="queue updates are for admin only")
    async with push_queue_to_mqtt(request, queue_id):
        async with request.app.ctx.queue_manager.async_queue_modify_context(queue_id) as queue:
            queue.move(source, target)
            return sanic.response.json({}, status=201)


@queue_blueprint.get("/<queue_id:str>/command/<command:([a-z]+).json>")
@openapi.definition(
    response=[
        openapi.definitions.Response({"application/json": {'is_playing': bool}},),
        openapi.definitions.Response('invalid command', status=400),
        openapi.definitions.Response('admin required', status=403),
    ]
)
async def queue_command(request, queue_id, command):
    if not request.ctx.is_admin:
        raise sanic.exceptions.Forbidden(message="commands are for admin only")
    if command not in {'play', 'stop'}:
        raise sanic.exceptions.NotFound(message='invalid command')
    async with push_queue_to_mqtt(request, queue_id):
        async with request.app.ctx.queue_manager.async_queue_modify_context(queue_id) as queue:
            getattr(queue, command)()
            return sanic.response.json({'is_playing': bool(queue.is_playing)})

# end Queue --------------------------------------------------------------------



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, workers=4, dev=True, access_log=True, auto_reload=True)
