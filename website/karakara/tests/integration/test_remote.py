from karakara.tests.conftest import unfinished

import re
from bs4 import BeautifulSoup
import socket, threading


@unfinished
def test_remote_control(app):
    """
    Connect to socketserver - unfortunately with a plain tcp socket rather than a websocket
    Load up remote page.
    Press remote buttons
    Assert socket receives the correct message
    """
    connected = True
    def conect_socket():
        def connection(sock):
            print("connected: test")
            while connected:
                data_recv = sock.recv(4098)
                if not data_recv:
                    break
                print("message recived: {0}".format(data_recv))
            print("disconnected: thats all folks")
            sock.close()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 9872))
        thread = threading.Thread(target=connection, args=(sock,))
        thread.daemon=True
        thread.start()
    
    def press_button(soup, button_text):
        response = app.get(soup.find('a', text=re.compile(button_text, flags=re.IGNORECASE))['href'])
        assert response.status_code==200
        #assert socket recives the message

    conect_socket()
    soup = BeautifulSoup(app.get('/remote').text)
    for button_name in ('play', 'pause', 'seek', 'stop', 'skip'):
        press_button(soup, button_name)
    connected = False
