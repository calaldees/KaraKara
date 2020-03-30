import aiohttp
from aiohttp import web

import logging
log = logging.getLogger(__name__)


class Server():

    def __init__(self, *args, **kwargs):
        pass

    @property
    def app(self):
        app = web.Application()
        app.router.add_get('/ws', self.websocket_handler)
        app.router.add_get("/", self.index_handler)
        return app

    async def index_handler(self, request):
        data = {'some': 'data'}
        #import pdb ; pdb.set_trace()
        return web.json_response(data)

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        log.info('websocket onConnected')
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.ERROR:
                log.error(ws.exception())
            await ws.close()  # close on any message - websockets are only for listening
        log.info('websocket onDisconnected')
        return ws


def aiohttp_app(argv):
    # python3 -m aiohttp.web -H 0.0.0.0 -P 9800 server:aiohttp_app
    return Server(argv).app
