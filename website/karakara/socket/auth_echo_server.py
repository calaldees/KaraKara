from .multisocket_server import ServerManager

import logging
log = logging.getLogger(__name__)

class AuthEchoServerManager(ServerManager):
    """
    A multi socket echo server that requires authentication
    
    After connecting the client should send a session key as their first message.
    an invalid key will result in disconnection.
    
    """
    clients_authenticated = []
    def __init__(self, authenticator, **options):
        self.authenticator = authenticator
        super().__init__(**options)
        log.info('{0} server setup'.format(__name__))
    def connect(self, client):
        log.info('connection %s connected'    % client.id)  # TODO - add logging of what type of client it was
    def disconnect(self, client):
        try:
            self.clients_authenticated.remove(client)
        except:
            pass
        log.info('connection %s disconnected' % client.id)
    def recv(self, data, source=None):
        if source and source not in self.clients_authenticated:
            key = str(data,'utf8')
            log.debug('authenticating {0}'.format(key))
            if self.authenticator(key):
                self.clients_authenticated.append(source)
                log.debug('authenticated')
            else:
                log.debug('rejected')
                source.close()
        else:
            try   : source_id = source.id
            except: source_id = None
            log.info('message {0} - {1}'.format(source_id,str(data,'utf8')))
            #if isinstance(data,str):
            #    data = data.encode('utf8')
            self.send(data, source)
    def stop(self):
        self.send(b'server_shutdown')
        super().stop()
