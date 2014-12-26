import httpagentparser

from pyramid.events import subscriber
from externals.lib.pyramid_helpers.events import SessionCreated

from externals.lib.log import log_event


@subscriber(SessionCreated)
def session_created(event):
    """
    On first connect, log the devices user agent
    """
    log_event(
        event.request,
        device=httpagentparser.detect(event.request.environ['HTTP_USER_AGENT']),
    )
