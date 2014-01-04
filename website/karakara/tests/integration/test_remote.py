from karakara.tests.conftest import unfinished

import re
from bs4 import BeautifulSoup
import socket, threading

class SocketClientTest():
    connected = True
    last_message = ''

    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 9872))
        thread = threading.Thread(target=self.connection, args=(sock,))
        thread.daemon=True
        thread.start()

    def connection(self, sock):
        print("connected: test")
        while self.connected:
            data_recv = sock.recv(4098)
            if not data_recv:
                break
            print("message recived: {0}".format(data_recv))
            self.last_message = data_recv
        print("disconnected: thats all folks")
        sock.close()


@unfinished
def test_remote_control(app):
    """
    Connect to socketserver - unfortunately with a plain tcp socket rather than a websocket
    Load up remote page.
    Press remote buttons
    Assert socket receives the correct message
    """
    client = SocketClientTest()
    
    def press_button(soup, button_text):
        url = soup.find('a', text=re.compile(button_text, flags=re.IGNORECASE))['href']
        print(url)
        response = app.get('/remote{0}'.format(url))
        assert response.status_code==200
        assert 'remote' in response.text.lower()
        assert client.last_message == button_text

    soup = BeautifulSoup(app.get('/remote').text)
    for button_name in ('play', 'pause', 'seek', 'stop', 'skip'):
        press_button(soup, button_name)

    client.connected = False
