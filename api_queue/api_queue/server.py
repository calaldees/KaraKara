from sanic import Sanic, response
from sanic_redis import SanicRedis

app = Sanic("karakara_queue")
#app.ctx.db = Database()


app.config.update(
    {
        'REDIS': "redis://redis:6379/0",
    }
)

redis = SanicRedis(config_name="REDIS")
redis.init_app(app)

# >>> import redis
# >>> r = redis.Redis(host='localhost', port=6379, db=0)
# >>> r.set('foo', 'bar')
# True
# >>> r.get('foo')
# b'bar'

# from redis import asyncio as aioredis
# async def main():
#     redis = aioredis.from_url("redis://localhost")
#     await redis.set("my-key", "value")
#     value = await redis.get("my-key")
#     print(value)


@app.get("/")
async def basic(request):
    #return response.text("foo")
    r = request.app.ctx.redis
    await r.set('key2', 'value2')
    result = await r.get('key2')
    return response.text(str(result))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337, workers=4, dev=True)
