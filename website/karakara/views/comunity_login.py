from pyramid.view import view_config

from externals.lib.social.social_login import login, logout

from . import web

import logging
log = logging.getLogger(__name__)


login_provider = None
user_store = None


@view_config(route_name='comunity_logout')
@web
def comunity_logout(request):
    return logout(request)


@view_config(route_name='comunity_login')
@web
def comunity_login(request):  # , login_provider=login_provider, user_store=user_store
    return login(request, login_provider, user_store)
