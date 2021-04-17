import re
from functools import partial

import bs4
def BeautifulSoup(markup):
    return bs4.BeautifulSoup(markup, "html.parser")

from . import admin_rights


def test_queue_home(app, queue):
    def _link_to(soup, link_text):
        try:
            return soup.find('a', text=re.compile(link_text, flags=re.IGNORECASE))['href']
        except:
            return None

    def get_queue_home_soup():
        return BeautifulSoup(app.get(f'/queue/{queue}').text)

    LINKS_ALL_USERS = {'search_tags', 'queue'}
    LINKS_ADMIN_USERS = {'remote', 'settings'}

    link_to = partial(_link_to, get_queue_home_soup())
    for menu_item in LINKS_ALL_USERS:
        assert link_to(menu_item)
    for menu_item in LINKS_ADMIN_USERS:
        assert not link_to(menu_item)

    with admin_rights(app, queue):
        link_to = partial(_link_to, get_queue_home_soup())
        for menu_item in LINKS_ALL_USERS | LINKS_ADMIN_USERS:
            assert link_to(menu_item)


def test_queue_home_not_exist(app, queue):
    response = app.get(f'/queue/not_a_queue', status=302)
    response = response.follow()
    assert response.request.path == '/'
    assert 'view.queue.not_exist' in response.text
