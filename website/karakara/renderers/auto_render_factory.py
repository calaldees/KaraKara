from pyramid.interfaces import IRendererFactory

from pyramid.response import Response

import logging
log = logging.getLogger(__name__)


class AutoRendererFactory:
    def __init__(self, info):
        """ Constructor: info will be an object having the
        following attributes: name (the renderer name), package
        (the package that was 'current' at the time the
        renderer was registered), type (the renderer type
        name), registry (the current application registry) and
        settings (the deployment settings dictionary). """
        log.info('init')

    def __call__(self, value, system):
        """ Call the renderer implementation with the value
        and the system value passed in as arguments and return
        the result (a string or unicode object).  The value is
        the return value of a view.  The system value is a
        dictionary containing available system values
        (e.g. view, context, and request). """
        log.info('call')
        #return Response(value)

def handle_before_render(event):
    log.info('before_render')