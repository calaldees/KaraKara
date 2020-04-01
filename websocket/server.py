from functools import cached_property
from collections import defaultdict
from itertools import chain
from urllib.parse import parse_qsl

import aiohttp
from aiohttp import web, WSCloseCode

import logging
log = logging.getLogger(__name__)


class Server():

    def __init__(self, *args, **kwargs):
        """
        Websocket broadcast via http

        ws://host:port/channel_name.ws
        GET /channel_name?message=hello
        POST /channel_name <message=hello>
        """
        pass

    @cached_property
    def app(self):
        app = web.Application()

        app['channels'] = defaultdict(set)
        # template_lookup = aiohttp_mako.setup(
        #     app,
        #     directories=['.'],
        #     input_encoding='utf-8',
        #     output_encoding='utf-8',
        #     default_filters=['decode.utf8'],
        # )
        with open('index.html', 'rt', encoding='utf-8') as filehandle:
            self.template_index = filehandle.read()

        app.router.add_get("/", self.handle_index)
        app.router.add_get("/{channel}.ws", self.handle_channel_websocket)
        app.router.add_route("*", "/{channel}", self.handle_channel)
        app.on_shutdown.append(self.on_shutdown)

        return app

    async def on_shutdown(self, app):
        for ws in tuple(chain.from_iterable(app['channels'].values())):
            await ws.close(code=WSCloseCode.GOING_AWAY, message='shutdown')

    #@aiohttp_mako.template('index.html')
    async def handle_index(self, request):
        if request.headers['accept'].startswith('text/html'):
            return web.Response(text=self.template_index, content_type='text/html')
        data = {
            'channels': {
                channel_name: len(clients)
                for channel_name, clients in request.app['channels'].items()
            },
        }
        return web.json_response(data)

    async def handle_channel(self, request):
        channel_name = request.match_info['channel']
        channel = request.app['channels'][channel_name]
        data = {**dict(parse_qsl(request.query_string)), **await request.post()}
        message = data.get('message', '')
        for ws in channel:
            await ws.send_str(message)
        return web.json_response({
            'message': message,
            'recipients': len(channel),
        })

    async def handle_channel_websocket(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        channel_name = request.match_info['channel']
        log.info(f'websocket onConnected {request.remote=} {channel_name=}')
        channel = request.app['channels'][channel_name]
        channel.add(ws)
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.ERROR:
                    log.error(ws.exception())
                await ws.send_str('This service is for listening only - closing connection')
                await ws.close()
        finally:
            channel.remove(ws)
        log.info(f'websocket onDisconnected {request.remote=} {channel_name=}')
        return ws


def aiohttp_app(argv):
    # python3 -m aiohttp.web -H 0.0.0.0 -P 9800 server:aiohttp_app
    return Server(argv).app
