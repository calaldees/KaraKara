## -*- coding: utf-8 -*-

import pytest

import bs4
def BeautifulSoup(markup):
    return bs4.BeautifulSoup(markup, "html.parser")

from . import admin_rights, temporary_settings


def test_queue_track_list_print_all(app, queue, tracks):
    """
    Track list displays all tracks in one giant document
    Used for printing
    """
    response = app.get(f'/queue/{queue}/track_list', expect_errors=True)
    assert response.status_code == 403

    with admin_rights(app, queue):
        response = app.get(f'/queue/{queue}/track_list')
        for text in ['track 1', 'track 2', 'track 3', 'wildcard']:
            assert text in response.text

        # The list should be sorted
        # The sorting is quite complex and combines multiple keys
        # This test is a loose assertion that the list is in category order
        soup = BeautifulSoup(response.text)
        def get_category(row_soup):
            try:
                return row_soup.find(**{'class': 'col_category'}).text
            except Exception:
                return ''
        categories = tuple(get_category(row_soup) for row_soup in soup.find_all(**{'class': ''}))
        categories = tuple(sorted(categories))


def test_queue_track_list_print_all_api(app, queue, tracks):
    # TODO: Security has been disbaled temporerally. This should be re-enabled ASAP
    #assert app.get('/track_list.json', expect_errors=True).status_code == 403
    with admin_rights(app, queue):
        data = app.get(f'/queue/{queue}/track_list?format=json').json['data']
        assert 'test track 2' in [title for track in data['list'] for title in track['tags']['title']]


def test_queue_track_list_all_tag_restrict(app, queue, tracks):
    with admin_rights(app, queue):
        def get_track_list_soup():
            return BeautifulSoup(app.get(f'/queue/{queue}/track_list').text)

        def get_settings():
            return app.get(f'/queue/{queue}/settings.json').json['data']['settings']
        settings = get_settings()
        assert settings['karakara.search.tag.silent_forced'] == []

        soup = get_track_list_soup()
        data_rows = soup.find_all('td', class_='col_id_short')
        assert len(data_rows) == 4

        #with patch.dict(settings, {'karakara.search.tag.silent_forced': ['category:anime']}):
        with temporary_settings(app, queue, {'karakara.search.tag.silent_forced': ['category:anime']}):
            soup = get_track_list_soup()
            data_rows = soup.find_all('td', class_='col_id_short')
            assert len(data_rows) == 2
            assert 't1' in soup.text
            assert 't2' in soup.text
            assert 't3' not in soup.text
