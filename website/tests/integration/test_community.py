import pytest
import json
import contextlib
from unittest.mock import patch

from calaldees.string_tools import random_string
from calaldees.social._login import ILoginProvider, ProviderToken
from calaldees.test import MultiMockOpen

from karakara.views.community import CommunityTrack
from karakara.views.community_login import social_login
from karakara.model import DBSession, commit
from karakara.model.model_community import CommunityUser
from karakara.model.model_tracks import Track


def login(app, name='TestUser'):
    social_token = DBSession.query(CommunityUser).filter(CommunityUser.name == name).one().tokens[0]

    class MockLoginProvider(ILoginProvider):
        provider_token = ProviderToken(social_token.provider, token=social_token.token, response={})  # this token should match tester@karakara.org.uk
        @property
        def html_include(self):
            return """<script>console.log('MockLoginProvider html_include');</script>"""
        def verify_cridentials(self, request):
            assert request.params.get('token') == 'token'
            return self.provider_token
        def aquire_additional_user_details(self, provider_token):
            assert False, 'in normal login flow this should not be called'

    with patch.dict(social_login.login_providers, {'test_provider': MockLoginProvider()}):
        response = app.get('/community/login?token=token')
        assert name in response.text
        assert 'MockLoginProvider' in response.text


def logout(app):
    response = app.get('/community/logout')
    assert 'login' in response.text.lower()


@contextlib.contextmanager
def community_login(app):
    login(app)
    yield
    logout(app)



# Tests ------------------------------------------------------------------------


def test_login_new_user(app, users):
    user_count = DBSession.query(CommunityUser).count()

    class MockLoginProvider(ILoginProvider):
        def __init__(self, additional_user_details):
            self.provider_token = ProviderToken('test_provider', token=random_string(), response={})
            self.additional_user_details = additional_user_details
        @property
        def html_include(self):
            return """"""
        def verify_cridentials(self, request):
            assert request.params.get('token') == 'token'
            return self.provider_token
        def aquire_additional_user_details(self, provider_token):
            assert provider_token == self.provider_token
            return self.additional_user_details

    mock_login_provider = MockLoginProvider({
        'name': 'NewUser',
        'email': 'newuser@gmail.com',
        'avatar_url': 'http://gravatar.com/abcde.png',
    })
    with patch.dict(social_login.login_providers, {'test_provider': mock_login_provider}):
        response = app.get('/community/login?token=token')
        assert 'NewUser' in response.text
        assert 'http://gravatar.com/abcde.png' in response.text
        assert 'glyphicon-warning-sign' in response.text, 'The new user should be waiting for approval'

    assert DBSession.query(CommunityUser).count() == user_count + 1

    logout(app)


def test_reject_unapproved(app):
    response = app.get('/community/list', status=403)
    assert 'Approved community users only' in response.text


def test_list(app, users, tracks):
    login(app)
    response = app.get('/community/list')
    for track in tracks:
        DBSession.add(track)  # Hu? why does this need to be attached to the session again?
        assert track.source_filename in response.text
    logout(app)


def test_list_invalidate(DBSession, app, users, tracks):
    """
    The 'community_list' view uses cache internally agressivly.
    The cache is based on the last_update() time of a track.
    Test is modifying a track in the database causes the community_list to
    produce the correct results.
    """
    login(app)

    def get_community_track_ids():
        return {track['id'] for track in app.get('/community/list.json').json['data']['tracks']}
    def add_track(track_id):
        track = Track()
        track.id = track_id
        DBSession.add(track)
        commit()
    def del_track(track_id):
        DBSession.query(Track).filter(Track.id == track_id).delete()
        commit()
    ids = get_community_track_ids()
    add_track('new')
    assert ids != get_community_track_ids()
    del_track('new')
    assert ids == get_community_track_ids()

    logout(app)


def test_community_track_render(app, users, tracks):
    login(app)

    # Static file data
    multi_mock_open = MultiMockOpen()
    multi_mock_open.add_handler(
        'track1source.txt',
        """
            title: Test Track 1 - TITLE EXTENDED
            artist: test artist
            category test category
        """
    )
    multi_mock_open.add_handler(
        'track1source.json',
        json.dumps({
            'scan': {
                'track1source.txt': {'relative': 'track1source.txt'},
                'track1source.avi': {'relative': 'track1source.avi'},
                'track1source.srt': {'relative': 'track1source.srt'},
            }
        })
    )
    multi_mock_open.add_handler(
        'track1source.srt',
        """
            subtitle content
        """
    )
    #multi_mock_open.add_handler(
    #    'test.srt',
    #    FileNotFoundError
    #)

    for track_url in (
            '/community/track/t1',
            '/community/track/t1.html',
            '/community/track/t1.html_template',
    ):
        # Make web request
        with patch.object(CommunityTrack, '_open', multi_mock_open.open):
            response = app.get(track_url)

        # Assert output
        for text in (
                'Test Track 1 - TITLE EXTENDED',
                'track1source',
                'subtitle content',
                'processed.mpg'  # Link to processed video is present
        ):
            assert text in response.text

    logout(app)


@pytest.mark.skip('unimplemented')
def test_community_settings(app, tracks, users, settings):
    """
    This is also testing tracks_all heavily in this flow
    """
    response = app.get('/community/settings', status=403)
    login(app)

    # Starting assertions
    response = app.get('/community/settings')
    assert 'karakara.search.tag.silent_forced' in response.text
    assert 'karakara.search.tag.silent_hidden' in response.text
    response = app.get('/track_list')
    assert 't1' in response.text.lower()
    assert 'wildcard' in response.text.lower()

    with patch.dict(settings, {'karakara.search.tag.silent_forced': []}):
        response = app.post('/community/settings', {
            'karakara.search.tag.silent_forced': 'lang:fr',
        })
        response = app.get('/community/settings')
        assert 'lang:fr' in response.text
        response = app.get('/track_list')
        assert 't1' not in response.text.lower()
        assert 'wildcard' in response.text.lower()

    with patch.dict(settings, {'karakara.search.tag.silent_hidden': []}):
        response = app.post('/community/settings', {
            'karakara.search.tag.silent_hidden': 'lang:fr',
        })
        response = app.get('/track_list')
        assert 't1' in response.text.lower()
        assert 'wildcard' not in response.text.lower()

        # TODO: Test only allowed setting updates are enfored
        #  hash settings -> attempt update disallowed setting -> check hash settings

    logout(app)


def test_community_processmedia_logs(app, registry_settings):
    response = app.get('/community/processmedia_log', status=403)

    login(app)

    multi_mock_open = MultiMockOpen()
    multi_mock_open.add_handler(
        'processmedia.log',
        """
2000-01-01 00:00:00,000 - __main__ - INFO - Info test
2001-01-01 00:00:00,000 - __main__ - WARNING - Warning test
2002-01-01 00:00:00,000 - __main__ - ERROR - Error test
"""
    )
    with patch.dict(registry_settings, {'static.processmedia2.log': 'processmedia.log'}):
        # rrrrrrr - kind of a hack using CommunityTrack._open .. but it works ..
        with patch.object(CommunityTrack, '_open', multi_mock_open.open):
            response = app.get('/community/processmedia_log?levels=WARNING,ERROR', expect_errors=True)

    assert 'Info test' not in response.text
    assert 'Warning test' in response.text
    assert 'Error test' in response.text

    logout(app)
