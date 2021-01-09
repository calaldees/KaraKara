import paho.mqtt.client as mqtt
import logging
log = logging.getLogger(__name__)


def _send_websocket_message(request, message):
    c = mqtt.Client()
    c.connect(request.queue.settings.get('karakara.websocket.host'))
    c.loop_start()

    msg = c.publish("karakara/queue/"+request.queue.id, message)
    msg.wait_for_publish()

def send_websocket_message(request, message):
    """Proxy for unittests mocking"""
    _send_websocket_message(request, message)
