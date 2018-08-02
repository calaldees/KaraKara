from pyramid.view import view_config

from calaldees.misc import convert_str
from . import action_ok, action_error, comunity_only

from ..model import DBSession
from ..model.model_comunity import ComunityUser


@view_config(
    context='karakara.traversal.ComunityUsersContext',
    request_method='GET',
)
@comunity_only
def community_users_view(request):
    return action_ok(data={'users': (user.to_dict() for user in DBSession.query(ComunityUser).all())})


@view_config(
    context='karakara.traversal.ComunityUsersContext',
    request_method='POST',
)
@comunity_only
def community_users_approve(request):
    user = DBSession.query(ComunityUser).filter(ComunityUser.id==int(request.params.get('user_id'))).one()
    user.approved = convert_str(request.params.get('approved', False), bool)
    return action_ok(message=f'{user.email} approved:{user.approved}')
