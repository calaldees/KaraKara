

import logging
log = logging.getLogger(__name__)

def handle_new_request(event):
    log.debug('request')
    #print('request' , event.request)


def handle_new_response(event):
    log.debug('response')
    #print('response', event.response)