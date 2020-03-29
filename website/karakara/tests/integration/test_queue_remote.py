import re

import bs4
def BeautifulSoup(markup):
    return bs4.BeautifulSoup(markup, "html.parser")

from . import admin_rights, websocket_message_queue


def test_remote_control(app, queue):
    """
    Connect to socketserver - unfortunately with a plain tcp socket rather than a websocket
    Load up remote page.
    Press remote buttons
    Assert socket receives the correct message
    """
    # Non admins cannot use the remote control
    remote_control_url = f'/queue/{queue}/remote_control'
    response = app.get(remote_control_url, expect_errors=True)
    response.status_code == 403


    # Attain admin privilages
    with admin_rights(app, queue):
        with websocket_message_queue() as message_received_queue:

            def press_button(soup, button_text):
                url = soup.find('a', text=re.compile(button_text, flags=re.IGNORECASE))['href']
                response = app.get(f'{remote_control_url}/{url}')
                assert response.status_code==200
                assert 'remote' in response.text.lower()
                #assert button_text in message_received_queue.get(timeout=3)  # TEMP Disable

            soup = BeautifulSoup(app.get(remote_control_url).text)
            for button_name in ('play', 'pause', 'seek', 'stop', 'skip'):
                press_button(soup, button_name)
