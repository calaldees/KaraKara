from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from calaldees.social.social_login import SocialLogin

import logging
log = logging.getLogger(__name__)


social_login = SocialLogin()


@view_config(
    context='karakara.traversal.CommunityLoginContext',
)
def community_login(request):  # , login_provider=login_provider, user_store=user_store
    if request.session.get('user'):
        raise HTTPFound(location='/community')
    return social_login.login(request)


@view_config(
    context='karakara.traversal.CommunityLogoutContext',
)
def community_logout(request):
    if not request.session.get('user'):
        raise HTTPFound(location='/community')
    return social_login.logout(request)
