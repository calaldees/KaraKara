import json
import random
import contextlib

import sanic

from ._utils import harden

from sanic.log import logger as log



app = sanic.Sanic("karakara_queue")

# OpenAPI3 Extension
from sanic_openapi import openapi, openapi3_blueprint
app.blueprint(openapi3_blueprint)  # Register - https://*/swagger/
# https://github.com/sanic-org/sanic-openapi/blob/main/examples/cars_oas3/blueprints/car.py
# https://sanic.dev/en/plugins/sanic-ext/openapi/autodoc.html#operation-level-yaml

app.config.update(
    {
        #'REDIS': "redis://redis:6379/0",
        #'MQTT': 'mqtt:1883',
        'TRACKS': 'tracks.json',
        'path_queue': '_queue_data',
    }
)

# Startup ----------------------------------------------------------------------

#@app.listener('main_process_start')
@app.listener('before_server_start')
async def tracks_load(_app: sanic.Sanic, _loop):
    log.info("[tracks] loading")
    with open(_app.config.get('TRACKS')) as filehandle:
        _app.ctx.tracks = harden(json.load(filehandle))



@app.listener('before_server_start')
async def aio_redis_configure(_app: sanic.Sanic, _loop):
    if _app.config.get('REDIS'):
        log.info("[redis] connecting")
        from redis import asyncio as aioredis
        _app.ctx.redis = await aioredis.from_url(_app.config.get('REDIS'))
#@app.listener('after_server_stop')
#async def aio_redis_close(_app, _loop):
    #log.info("[redis] closing")
    # TODO: gracefull close?
    #if _app.ctx.redis:
    #    await _app.ctx.redis.close()


@app.listener('before_server_start')
async def aio_mqtt_configure(_app: sanic.Sanic, _loop):
    mqtt = _app.config.get('MQTT')
    if isinstance(mqtt, str):
        log.info("[mqtt] connecting")
        from asyncio_mqtt import Client as MqttClient, MqttError
        _app.ctx.mqtt = MqttClient(mqtt)
    elif mqtt:  # normally pass-through for mock mqtt object
        _app.ctx.mqtt = mqtt



from .queue import QueueManagerCSVAsync, QueueItem, SettingsManager
@app.listener('before_server_start')
async def queue_manager(_app: sanic.Sanic, _loop):
    log.info("[queue_manager]")
    _app.ctx.settings_manager = SettingsManager(path=_app.config.get('path_queue'))
    _app.ctx.queue_manager = QueueManagerCSVAsync(path=_app.config.get('path_queue'), settings=_app.ctx.settings_manager)


# Middleware -------------------------------------------------------------------

# pytest debugging - This is needed to see exceptions on failed tests. DEBUG=True wont give me json exceptions. SO CLUMSY!
# https://sanic.dev/en/guide/best-practices/exceptions.html#custom-error-handling
class CustomErrorHandler(sanic.handlers.ErrorHandler):
    def default(self, request, exception):
        if isinstance(exception, sanic.exceptions.SanicException):
            return super().default(request, exception)
        import traceback
        return sanic.response.json({'exception': "".join(traceback.TracebackException.from_exception(exception).format())}, status=500)
app.error_handler = CustomErrorHandler()



@app.middleware("request")
async def attach_session_id_request(request):
    request.ctx.session_id = request.cookies.get("session_id") or str(random.random())
@app.middleware("response")
async def attach_session_id(request, response):
    if not request.cookies.get("session_id"):
        response.cookies["session_id"] = request.ctx.session_id


@contextlib.asynccontextmanager
async def push_queue_to_mqtt(request, queue_id):
    yield
    if hasattr(request.app.ctx, 'mqtt'):
        log.info(f"push_queue_to_mqtt {queue_id}")
        await request.app.ctx.mqtt.publish(f"karakara/room/{queue_id}/queue", request.app.ctx.queue_manager.for_json(queue_id), retain=True)


# Routes -----------------------------------------------------------------------

#@app.get("/")
#async def root(request):
#    redis = request.app.ctx.redis
#    await redis.set('key2', 'value2')
#    result = await redis.get('key2')
#    return sanic.response.text(str(result))


#@app.get("/queue/<queue_id:str>/tracks.json")
#async def tracks_from_memory(request):
#    return sanic.response.json(request.app.ctx.tracks)
@app.get("/queue/<queue_id:str>/tracks.json")
async def tracks_from_disk(request, queue_id):
    return await sanic.response.file(request.app.config.get('TRACKS'))
    # TODO: replace 302 redirect to static file from nginx? Could be useful to have this as a fallback?
@app.get("/queue/<queue_id:str>/queue.csv")
async def queue_csv(request, queue_id):
    return await sanic.response.file(request.app.ctx.queue_manager.path_csv(queue_id))
@app.get("/queue/<queue_id:str>/queue.json")
async def queue_json(request, queue_id):
    return sanic.response.json(request.app.ctx.queue_manager.for_json(queue_id))
@app.get("/queue/<queue_id:str>/settings.json")
async def queue_settings_json(request, queue_id):
    return sanic.response.json(request.app.ctx.settings_manager.get_json(queue_id))


@app.post("/queue/<queue_id:str>/")
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

@app.put("/queue/<queue_id:str>/")
async def update_queue_item(request, queue_id):
    try:
        queue_item_id_1 = float(request.args.get('queue_item_id_1'))
        queue_item_id_2 = float(request.args.get('queue_item_id_2'))
    except (ValueError, TypeError):
        raise sanic.exceptions.InvalidUsage(message="queue_item_id_1 and queue_item_id_2 args required", context=request.args)
    if request.ctx.session_id != 'admin':
        raise sanic.exceptions.Forbidden(message="queue updates are for admin only")
    async with push_queue_to_mqtt(request, queue_id):
        async with request.app.ctx.queue_manager.async_queue_modify_context(queue_id) as queue:
            queue.move(queue_item_id_1, queue_item_id_2)
            return sanic.response.json({})

@app.delete("/queue/<queue_id:str>/")
async def delete_queue_item(request, queue_id):
    try:
        queue_item_id = float(request.args.get('queue_item_id'))
    except (ValueError, TypeError):
        raise sanic.exceptions.InvalidUsage(message="queue_item_id arg required")
    async with push_queue_to_mqtt(request, queue_id):
        async with request.app.ctx.queue_manager.async_queue_modify_context(queue_id) as queue:
            _, queue_item = queue.get(queue_item_id)
            if not queue_item:
                raise sanic.exceptions.NotFound()
            if queue_item.session_id != request.ctx.session_id and request.ctx.session_id != 'admin':
                raise sanic.exceptions.Forbidden(message="queue_item.session_id does not match session_id")
            queue.delete(queue_item_id)
            return sanic.response.json(queue_item.asdict())

@app.get("/queue/<queue_id:str>/command/<command:str>")
async def queue_command(request, queue_id, command):
    if request.ctx.session_id != 'admin':
        raise sanic.exceptions.Forbidden(message="commands are for admin only")
    if command not in {'play', 'stop'}:
        raise sanic.exceptions.NotFound(message='invalid command')
    async with push_queue_to_mqtt(request, queue_id):
        async with request.app.ctx.queue_manager.async_queue_modify_context(queue_id) as queue:
            getattr(queue, command)()
            return sanic.response.json({'is_playing': queue.is_playing()})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, workers=4, dev=True, access_log=True, auto_reload=True)
