from unittest.mock import patch

from externals.lib.social._login import ILoginProvider, ProviderToken

from karakara.model import DBSession
from karakara.model.model_comunity import ComunityUser


def login(app, name='TestUser'):
    social_token = DBSession.query(ComunityUser).filter(ComunityUser.name == name).one().tokens[0]

    class MockLoginProvider(ILoginProvider):
        provider_token = ProviderToken(social_token.provider, token=social_token.token)  # this token should match tester@karakara.org.uk
        def verify_cridentials(self, request):
            assert request.params.get('token') == 'token'
            return self.provider_token
        def aquire_additional_user_details(self, provider_token):
            assert provider_token == self.provider_token
            return social_token.data

    from karakara.views import comunity_login
    with patch.object(comunity_login, 'login_provider', MockLoginProvider()):
        response = app.get('/comunity/login?token=token')
        assert name in response.text


def logout(app):
    response = app.get('/comunity/logout')
    assert 'login' in response.text.lower()


def test_reject_unapproved(app):
    response = app.get('/comunity/list', expect_errors=True)
    assert response.status_code == 403
    assert 'Approved comunity users only' in response.text


def test_list(app, users, tracks):
    login(app)
    response = app.get('/comunity/list')
    for track in tracks:
        DBSession.add(track)
        assert track.title in response.text
    logout(app)
