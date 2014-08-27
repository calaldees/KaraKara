import hashlib
import time

from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

from externals.lib.social._login import FacebookLogin

from ..model import DBSession, commit
from ..model.model_comunity import ComunityUser, SocialToken
from . import web, action_ok, action_error
from ..templates import helpers as h

import logging
log = logging.getLogger(__name__)


@view_config(route_name='comunity_logout')
@web
def comunity_logout(request):
    request.session['comunity'] = {}
    return action_ok()


@view_config(route_name='comunity_login')
@web
def comunity_login(request):
    user = None
    provider_token = None

    # Auto login if no service keys are provided
    if request.registry.settings.get('karakara.server.mode') == 'development' and not request.registry.settings.get('facebook.secret'):
        request.session['comunity'] = {
            'username': 'developer',
            'avatar'  : '{0}{1}'.format(h.path.static, 'dev_avatar.png'),
            'approved': True,
        }
        return action_ok()

    login_provider = FacebookLogin()

    # Step 1 - Direct user to 3rd party login dialog ---------------------------
    if not request.session.get('comunity'):
        if 'csrf_token' not in request.session:
            sha1_hash = hashlib.sha1()
            sha1_hash.update(str(time.time()).encode('utf-8'))
            request.session['csrf_token'] = sha1_hash.hexdigest()
        data = login_provider.display_login_dialog(request)
        return action_ok(data=data)  # template will be rendered with this data

    # Step 2 - Lookup full 3rd party access_token with token from dialog -------
    provider_token = login_provider.verify_cridentials(request)

    if not provider_token:
        error_message = 'error verifying cridentials'
        log.error(error_message)
        raise action_error(message=error_message)

    # Step 3 - Lookup local user_id OR create local user with details from 3rd party service
    try:
        user = DBSession.query(ComunityUser).join(SocialToken).filter(
            SocialToken.provider == provider_token.provider,
            SocialToken.token == provider_token.token,
        ).one()
    except NoResultFound:
        user = ComunityUser()

        #if provider_token.provider == 'facebook':
        user_data = login_provider.aquire_additional_user_details(provider_token)
        user.tokens.append(SocialToken(
            token=provider_token.token,
            provider=provider_token.provider,
            data=user_data,
        ))
        #user.name = '{first_name} {last_name}'.format(**user_data)

        DBSession.add(user)
        commit()
        DBSession.add(user)
        request.session['comunity'] = {'id': user.id}

    # Step 4 - lookup local user and set session details
    user_id = request.session.get('comunity', {}).get('id')
    try:
        # lookup new user or use user aquired in previous step
        user = user or DBSession.query(ComunityUser).filter(ComunityUser.id == user_id).one()
        request.session['comunity'] = {
            'username'  : user.name,
            'email'     : user.email,
            'provider'  : provider_token.provider,
            'avatar_url': user_data.get('avatar_url'),
            'approved'  : user.approved,
        }
    except NoResultFound:
        error_message = 'no user {0}'.format(user_id)
        request.session['comunity'] = {}
        log.error(error_message)
        raise action_error(message=error_message)

    return action_ok()
