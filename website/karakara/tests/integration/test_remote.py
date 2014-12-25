import re
from bs4 import BeautifulSoup
import socket

from multiprocessing import Process, Queue


def test_remote_control(app):
    """
    Connect to socketserver - unfortunately with a plain tcp socket rather than a websocket
    Load up remote page.
    Press remote buttons
    Assert socket receives the correct message
    """
    # Non admins cannot use the remote control
    response = app.get('/remote', expect_errors=True)
    response.status_code == 403

    # Attain admin privilages
    response_json = app.get('/admin.json').json
    assert response_json['identity']['admin']

    def connection(sock, message_received_queue):
        while True:
            data_recv = sock.recv(4098)
            if not data_recv:
                break
            message_received_queue.put(data_recv.decode('utf-8'))
        sock.close()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 9872))
    message_received_queue = Queue()
    client_listener_process = Process(target=connection, args=(sock, message_received_queue,))
    client_listener_process.daemon = True
    client_listener_process.start()

    def press_button(soup, button_text):
        url = soup.find('a', text=re.compile(button_text, flags=re.IGNORECASE))['href']
        response = app.get('/remote{0}'.format(url))
        assert response.status_code==200
        assert 'remote' in response.text.lower()
        assert button_text in message_received_queue.get(timeout=1)

    soup = BeautifulSoup(app.get('/remote').text)
    for button_name in ('play', 'pause', 'seek', 'stop', 'skip'):
        press_button(soup, button_name)

    client_listener_process.terminate()
    client_listener_process.join()

    # Revolk admin privilages
    response_json = app.get('/admin.json').json
    assert not response_json['identity']['admin']
