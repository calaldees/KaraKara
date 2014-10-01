from pyramid.view import view_config

from externals.lib.social.social_login import SocialLogin

from . import web

import logging
log = logging.getLogger(__name__)


social_login = SocialLogin()


@view_config(route_name='comunity_logout')
@web
def comunity_logout(request):
    return social_login.logout(request)


@view_config(route_name='comunity_login')
@web
def comunity_login(request):  # , login_provider=login_provider, user_store=user_store
    return social_login.login(request)
