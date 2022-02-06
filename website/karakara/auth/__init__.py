from calaldees.social._login import IUserStore

from sqlalchemy.orm.exc import NoResultFound

from ..model import DBSession, commit
from ..model.model_community import CommunityUser, SocialToken

from ..templates import helpers as h

import logging
log = logging.getLogger(__name__)


class CommunityUserStore(IUserStore):

    def get_user_from_token(self, provider_token):
        try:
            return DBSession.query(CommunityUser).join(SocialToken).filter(
                SocialToken.provider == provider_token.provider,
                SocialToken.token == provider_token.token,
            ).one()
        except NoResultFound:
            return None

    def create_user(self, provider_token, name=None, email=None, **user_data):
        user = CommunityUser()
        user.name = name or user_data.get('username')
        user.email = email
        # The first user created is always automatically an admin
        # TODO: A test for this
        user.approved = False if DBSession.query(CommunityUser).count() else True

        user.tokens.append(SocialToken(
            token=provider_token.token,
            provider=provider_token.provider,
            data=user_data,
        ))
        #user.name = f"{user_data['first_name']} {user_data['last_name']}'
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


class NullCommunityUserStore(IUserStore):
    def get_user_from_token(self, provider_token):
        return True

    def user_to_session_dict(self, user):
        return {
            'username': 'developer',
            'approved': True,
            'avatar': f'{h.path.static}dev_avatar.png',
        }

