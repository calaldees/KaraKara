from sanic import Sanic, response

import logging
log = logging.getLogger(__name__)


app = Sanic("karakara_queue")


app.config.update(
    {
        'REDIS': "redis://redis:6379/0",
        'MQTT': 'mqtt:1883',
    }
)


# sanic_redis uses `aioredis` and this has been deprecated`
#from sanic_redis import SanicRedis
#redis = SanicRedis(config_name="REDIS")
#redis.init_app(app)

from redis import asyncio as aioredis
@app.listener('before_server_start')
async def aio_redis_configure(_app: Sanic, _loop):
    log.info("[redis] connecting")
    _app.ctx.redis = await aioredis.from_url(_app.config.get('REDIS'))
@app.listener('after_server_stop')
async def aio_redis_close(_app, _loop):
    log.info("[redis] closing")
    # TODO: gracefull close?
    #if _app.ctx.redis:
    #    await _app.ctx.redis.close()


from asyncio_mqtt import Client as MqttClient, MqttError
@app.listener('before_server_start')
async def aio_mqtt_configure(_app: Sanic, _loop):
    log.info("[mqtt] connecting")
    _app.ctx.mqtt = MqttClient(_app.config.get('MQTT'))
# await request.app.ctx.mqtt.publish(topic, message, qos=1)
#"karakara/room/"+request.queue.id+"/"+topic, message, retain=True


@app.get("/")
async def root(request):
    redis = request.app.ctx.redis
    await redis.set('key2', 'value2')
    result = await redis.get('key2')
    return response.text(str(result))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337, workers=4, dev=True)
