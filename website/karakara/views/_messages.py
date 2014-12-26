from decorator import decorator

from externals.lib.pyramid_helpers import request_from_args

from ..model.model_messages import Message


import logging
log = logging.getLogger(__name__)


def overlay_messages():
    """
    """
    def _overlay_messages(target, *args, **kwargs):
        request = request_from_args(args)
        if 'internal_request' in request.matchdict:  # Abort if internal call
            return target(*args, **kwargs)

        #log.debug('Overlay messages test')
        result = target(*args, **kwargs)

        return result

    return decorator(_overlay_messages)
