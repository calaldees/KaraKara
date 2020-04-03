import requests


def _send_websocket_message(request, message):
    """
    Websockets are handled by 'websocket' container
    """
    raise NotImplementedError()
def send_websocket_message(request, message):
    """Proxy for unittests mocking"""
    _send_websocket_message(request, message)
