from pyramid.view import view_config

from calaldees.string_convert import convert_str
from . import action_ok, community_only

from ..model import DBSession
from ..model.model_community import CommunityUser


@view_config(
    context='karakara.traversal.CommunityUsersContext',
    request_method='GET',
)
@community_only
def community_users_view(request):
    return action_ok(data={'users': (user.to_dict() for user in DBSession.query(CommunityUser).all())})


@view_config(
    context='karakara.traversal.CommunityUsersContext',
    request_method='POST',
)
@community_only
def community_users_approve(request):
    user = DBSession.query(CommunityUser).filter(CommunityUser.id==int(request.params.get('user_id'))).one()
    user.approved = convert_str(request.params.get('approved', False), bool)
    return action_ok(message=f'{user.email} approved:{user.approved}')
