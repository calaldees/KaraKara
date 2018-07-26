from calaldees..social._login import IUserStore

from sqlalchemy.orm.exc import NoResultFound

from ..model import DBSession, commit
from ..model.model_comunity import ComunityUser, SocialToken

from ..templates import helpers as h

import logging
log = logging.getLogger(__name__)


class ComunityUserStore(IUserStore):

    def get_user_from_token(self, provider_token):
        try:
            return DBSession.query(ComunityUser).join(SocialToken).filter(
                SocialToken.provider == provider_token.provider,
                SocialToken.token == provider_token.token,
            ).one()
        except NoResultFound:
            return None

    def create_user(self, provider_token, name=None, email=None, **user_data):
        user = ComunityUser()
        user.name = name
        user.email = email

        user.tokens.append(SocialToken(
            token=provider_token.token,
            provider=provider_token.provider,
            data=user_data,
        ))
        #user.name = '{first_name} {last_name}'.format(**user_data)
        log.debug(' - '.join(('create_user', str(provider_token), str(user_data))))

        DBSession.add(user)
        commit()

    def user_to_session_dict(self, user):
        return {
            'username': user.name,
            'email': user.email,
            #'provider'  : provider_token.provider,
            'avatar_url': user.tokens[0].data.get('avatar_url'),
            'approved': user.approved,
        }


class NullComunityUserStore(IUserStore):
    def get_user_from_token(self, provider_token):
        return True

    def user_to_session_dict(self, user):
        return {
            'username': 'developer',
            'approved': True,
            'avatar': '{0}{1}'.format(h.path.static, 'dev_avatar.png'),
        }

