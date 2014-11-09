from ..model import DBSession, commit
from ..model.model_comunity import ComunityUser


def list_pending_users():
    return [user.email for user in DBSession.query(ComunityUser).filter(ComunityUser.approved == False)]


def approve_user(email, auto_commit=True):
    """
    Example user

    make shell_production
    from karakara.auth.utils import * ; list_pending_users()
    ['...', '...']
    approve_user('user@email.com')

    User will need to logout and login again once approved
    """
    user = DBSession.query(ComunityUser).filter(ComunityUser.email == email).one()
    user.approved = True
    if auto_commit:
        commit()
