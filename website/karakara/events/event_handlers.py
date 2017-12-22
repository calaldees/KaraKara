import httpagentparser

from pyramid.events import subscriber
from externals.lib.pyramid_helpers.events import SessionCreated


known_ip_address = set()


@subscriber(SessionCreated)
def session_created(event):
    """
    On first connect, log the devices user agent
    """
    # Quick hack to prevent flooding of event logs for
    #  - Users with cookies turned off (hopefully not to many of these in the real world).
    #  - Test users that create a new request every time.
    ip = event.request.environ.get('REMOTE_ADDR')
    if ip in known_ip_address:
        return
    known_ip_address.add(ip)

    event.request.log_event(
        device=httpagentparser.detect(event.request.environ.get('HTTP_USER_AGENT')),
    )
