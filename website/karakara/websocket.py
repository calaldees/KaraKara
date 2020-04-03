import os
import requests

from calaldees.url import build_url

import logging
log = logging.getLogger(__name__)


def _send_websocket_message(request, message):
    """
    Websockets are handled by 'websocket' container
    """
    url = build_url(
        host=request.queue.settings.get('karakara.websocket.host'),
        port=request.queue.settings.get('karakara.websocket.port'),
        path=request.queue.id,
        query_string_dict=dict(message=message),
    )
    log.info(url)
    response = requests.get(url, timeout=1)
    if response.status_code < 200 or response.status_code >= 300:
        log.error(f'Unable to send websocket message {url}')
def send_websocket_message(request, message):
    """Proxy for unittests mocking"""
    _send_websocket_message(request, message)
