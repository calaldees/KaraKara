import re

import bs4
def BeautifulSoup(markup):
    return bs4.BeautifulSoup(markup, "html.parser")

from . import admin_rights


def test_remote_control(app, queue, mock_send_websocket_message):
    """
    Connect to socketserver - unfortunately with a plain tcp socket rather than a websocket
    Load up remote page.
    Press remote buttons
    Assert socket receives the correct message
    """
    # Non admins cannot use the remote control
    remote_control_url = f'/queue/{queue}/remote_control'
    response = app.get(remote_control_url, status=403)

    # Attain admin privilages
    with admin_rights(app, queue):
        def press_button(soup, button_text):
            url = soup.find('a', text=re.compile(button_text, flags=re.IGNORECASE))['href']
            response = app.get(f'{remote_control_url}/{url}', status=200)
            assert 'remote' in response.text.lower()
            assert button_text in mock_send_websocket_message.call_args.args[2]
            mock_send_websocket_message.reset_mock()

        soup = BeautifulSoup(app.get(remote_control_url).text)
        for button_name in ('play', 'pause', 'seek', 'stop', 'skip'):
            press_button(soup, button_name)
