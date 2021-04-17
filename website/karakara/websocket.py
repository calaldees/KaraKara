import paho.mqtt.client as mqtt
from pyramid.request import Request
import logging
log = logging.getLogger(__name__)


def _send_websocket_message(request: Request, topic: str, message: str, retain: bool) -> None:
    c = mqtt.Client()
    c.connect(request.registry.settings['karakara.websocket.host'])
    c.loop_start()

    msg = c.publish("karakara/room/"+request.queue.id+"/"+topic, message, retain=retain)
    msg.wait_for_publish()

def send_websocket_message(request: Request, topic: str, message: str, retain: bool=False) -> None:
    """Proxy for unittests mocking"""
    _send_websocket_message(request, topic, message, retain)
