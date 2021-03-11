import paho.mqtt.client as mqtt
import logging
log = logging.getLogger(__name__)


def _send_websocket_message(request, topic, message, retain):
    c = mqtt.Client()
    c.username_pw_set(
        request.registry.settings['karakara.websocket.username'],
        request.registry.settings['karakara.websocket.password']
    )
    c.connect(request.registry.settings['karakara.websocket.host'])
    c.loop_start()

    msg = c.publish("karakara/room/"+request.queue.id+"/"+topic, message, retain=retain)
    msg.wait_for_publish()

def send_websocket_message(request, topic, message, retain=False):
    """Proxy for unittests mocking"""
    _send_websocket_message(request, topic, message, retain)
