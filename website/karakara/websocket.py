import paho.mqtt.client as mqtt
import logging
log = logging.getLogger(__name__)


def _send_websocket_message(request, channel, message, retain):
    c = mqtt.Client()
    c.username_pw_set("karakara", "aeyGGrYJ")
    c.connect(request.queue.settings.get('karakara.websocket.host'))
    c.loop_start()

    msg = c.publish("karakara/room/"+request.queue.id+"/"+channel, message, retain=retain)
    msg.wait_for_publish()

def send_websocket_message(request, channel, message, retain=False):
    """Proxy for unittests mocking"""
    _send_websocket_message(request, channel, message, retain)
