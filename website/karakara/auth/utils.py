from ..model import DBSession, commit
from ..model.model_community import CommunityUser


def list_pending_users():
    return [user.email for user in DBSession.query(CommunityUser).filter(CommunityUser.approved==False)]


def approve_user(email=None, auto_commit=True):
    """
    Example user

    make shell_production
    from karakara.auth.utils import * ; list_pending_users()
    ['...', '...']
    approve_user('user@email.com')
    or
    approve_user()  # for all unapproved users

    User will need to logout and login again once approved
    """
    query = DBSession.query(CommunityUser)
    if email:
        query = query.filter(CommunityUser.email == email)
    for user in query.all():
        user.approved = True
    if auto_commit:
        commit()
