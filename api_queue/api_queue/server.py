import json

import sanic

from ._utils import harden

import logging
log = logging.getLogger(__name__)


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
        'TRACKS': 'tracks.json'
    }
)


# sanic_redis uses `aioredis` and this has been deprecated`
#from sanic_redis import SanicRedis
#redis = SanicRedis(config_name="REDIS")
#redis.init_app(app)

# Startup ----------------------------------------------------------------------

@app.listener('before_server_start')
async def aio_redis_configure(_app: sanic.Sanic, _loop):
    log.info("[redis] connecting")
    if _app.config.get('REDIS'):
        from redis import asyncio as aioredis
        _app.ctx.redis = await aioredis.from_url(_app.config.get('REDIS'))
@app.listener('after_server_stop')
async def aio_redis_close(_app, _loop):
    log.info("[redis] closing")
    # TODO: gracefull close?
    #if _app.ctx.redis:
    #    await _app.ctx.redis.close()


@app.listener('before_server_start')
async def aio_mqtt_configure(_app: sanic.Sanic, _loop):
    log.info("[mqtt] connecting")
    if _app.config.get('MQTT'):
        from asyncio_mqtt import Client as MqttClient, MqttError
        _app.ctx.mqtt = MqttClient(_app.config.get('MQTT'))
# await request.app.ctx.mqtt.publish(topic, message, qos=1)
#"karakara/room/"+request.queue.id+"/"+topic, message, retain=True


@app.listener('before_server_start')
async def tracks_load(_app: sanic.Sanic, _loop):
    log.info("[tracks] loading")
    with open(_app.config.get('TRACKS')) as filehandle:
        _app.ctx.tracks = harden(json.load(filehandle))



from .queue import QueueManagerCSVAsync, QueueItem, SettingsManager
@app.listener('before_server_start')
async def queue_manager(_app: sanic.Sanic, _loop):
    log.info("[queue_manager]")
    _app.ctx.settings_manager = SettingsManager()
    _app.ctx.queue_manager = QueueManagerCSVAsync(settings=_app.ctx.settings_manager)


# Queue ------------------------------------------------------------------------

#@app.middleware("request")
#async def extract_user(request):
#    request.ctx.user = await extract_user_from_request(request)

# add queue to request
# auto output to mqtt on queue.modify




# Routes -----------------------------------------------------------------------

@app.get("/")
async def root(request):
    redis = request.app.ctx.redis
    await redis.set('key2', 'value2')
    result = await redis.get('key2')
    return sanic.response.text(str(result))


#@app.get("/tracks/")
#async def tracks(request):
#    return sanic.response.json(request.app.ctx.tracks)


@app.get("/queue/<queue_id:str>/tracks/")
async def tracks(request, queue_id):
    return await sanic.response.file(request.app.config.get('TRACKS'))
    # TODO: replace 302 redirect to static file from nginx? Could be useful to have this as a fallback?

@app.get("/queue/<queue_id:str>/queue_items.csv")
async def queue_items_csv(request, queue_id):
    return await sanic.response.file(request.app.ctx.queue_manager.path_csv(queue_id))
@app.get("/queue/<queue_id:str>/queue_items.json")
async def queue_items_json(request, queue_id):
    return sanic.response.json(request.app.ctx.queue_manager.for_json(queue_id))
@app.get("/queue/<queue_id:str>/settings.json")
async def queue_settings_json(request, queue_id):
    return sanic.response.json(request.app.ctx.settings_manager.get_json(queue_id))



@app.get("/queue/<queue_id:str>/add_test/")
async def add_test(request, queue_id):
    """This is a simple foo handler

    Now we will add some more details

    openapi:
    ---
    operationId: fooDots
    tags:
      - one
      - two
    parameters:
      - name: limit
        in: query
        description: How many items to return at one time (max 100)
        required: false
        schema:
          type: integer
          format: int32
    responses:
      '200':
        description: Just some dots
    """
    #return sanic.response.text('ok')
    async with request.app.ctx.queue_manager.async_queue_modify_context(queue_id) as queue:
        queue.add(QueueItem('Track7', 60, 'TestSession7'))
        return sanic.response.text('ok')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, workers=4, dev=True, access_log=True, auto_reload=True)
