import pytest
import json
from unittest.mock import patch

from externals.lib.social._login import ILoginProvider, ProviderToken
from externals.lib.test import MultiMockOpen

from karakara.views.comunity import ComunityTrack
from karakara.model import DBSession
from karakara.model.model_comunity import ComunityUser


def login(app, name='TestUser'):
    social_token = DBSession.query(ComunityUser).filter(ComunityUser.name == name).one().tokens[0]

    class MockLoginProvider(ILoginProvider):
        provider_token = ProviderToken(social_token.provider, token=social_token.token, response={})  # this token should match tester@karakara.org.uk
        @property
        def html_include(self):
            return """<script>console.log('MockLoginProvider html_include');</script>"""
        def verify_cridentials(self, request):
            assert request.params.get('token') == 'token'
            return self.provider_token
        def aquire_additional_user_details(self, provider_token):
            assert provider_token == self.provider_token
            return social_token.data

    from karakara.views.comunity_login import social_login
    with patch.dict(social_login.login_providers, {'test_provider': MockLoginProvider()}):
        response = app.get('/comunity/login?token=token')
        assert name in response.text
        assert 'MockLoginProvider' in response.text


def logout(app):
    response = app.get('/comunity/logout')
    assert 'login' in response.text.lower()


# Tests ------------------------------------------------------------------------

def test_reject_unapproved(app):
    response = app.get('/comunity/list', expect_errors=True)
    assert response.status_code == 403
    assert 'Approved comunity users only' in response.text


def test_list(app, users, tracks):
    login(app)
    response = app.get('/comunity/list')
    for track in tracks:
        DBSession.add(track)  # Hu? why does this need to be attached to the session again?
        assert track.source_filename in response.text
    logout(app)


@pytest.mark.xfail  # Temp during refactoring
def test_track(app, users, tracks):
    login(app)

    # Static file data
    multi_mock_open = MultiMockOpen()
    multi_mock_open.add_handler(
        'tags.txt',
        """
            title: Test Track 1 - TITLE EXTENDED
            artist: test artist
            category test category
        """
    )
    multi_mock_open.add_handler(
        'sources.json',
        json.dumps({
            'test.avi': {},
            'test.ssa': {},
            'test.srt': {},
        })
    )
    multi_mock_open.add_handler(
        'test.ssa',
        """
            subtitle content
        """
    )
    multi_mock_open.add_handler(
        'test.srt',
        FileNotFoundError
    )


    # Make web request
    with patch.object(ComunityTrack, '_open', multi_mock_open.open):
        response = app.get('/comunity/track/t1')

    # Assert output
    for text in (
        'Test Track 1 - TITLE EXTENDED',
        'track1source',
        'subtitle content',
        'processed.mpg'  # Link to processed video is present
    ):
        assert text in response.text

    logout(app)

@pytest.mark.xfail  # Temp during refactoring
def test_settings(app, tracks, users, settings):
    """
    This is also testing tracks_all heavily in this flow
    """
    response = app.get('/comunity/settings', expect_errors=True)
    assert response.status_code == 403
    login(app)

    # Starting assertions
    response = app.get('/comunity/settings')
    assert 'karakara.search.tag.silent_forced' in response.text
    assert 'karakara.search.tag.silent_hidden' in response.text
    response = app.get('/track_list')
    assert 't1' in response.text.lower()
    assert 'wildcard' in response.text.lower()

    with patch.dict(settings, {'karakara.search.tag.silent_forced': []}):
        response = app.post('/comunity/settings', {
            'karakara.search.tag.silent_forced': 'lang:fr',
        })
        response = app.get('/comunity/settings')
        assert 'lang:fr' in response.text
        response = app.get('/track_list')
        assert 't1' not in response.text.lower()
        assert 'wildcard' in response.text.lower()

    with patch.dict(settings, {'karakara.search.tag.silent_hidden': []}):
        response = app.post('/comunity/settings', {
            'karakara.search.tag.silent_hidden': 'lang:fr',
        })
        response = app.get('/track_list')
        assert 't1' in response.text.lower()
        assert 'wildcard' not in response.text.lower()

        # TODO: Test only allowed setting updates are enfored
        #  hash settings -> attempt update disallowed setting -> check hash settings

    logout(app)
