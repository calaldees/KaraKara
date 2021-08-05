import pytest

from karakara.model import DBSession, commit

from karakara.model.model_community import CommunityUser, SocialToken


@pytest.fixture(scope="session")
def users(request):
    """
    """
    users = []

    user = CommunityUser()
    user.name = 'TestUser'
    user.email = 'tester@karakara.uk'
    user.approved = True
    token = SocialToken()
    token.token = 'abcdefg'
    token.provider = 'test_provider'
    token.data = {'avatar_url': 'avatar1.png'}
    user.tokens.append(token)
    DBSession.add(user)
    users.append(user)

    user = CommunityUser()
    user.name = 'UnknownUser'
    user.email = 'unknown@karakara.uk'
    user.approved = False
    token = SocialToken()
    token.token = '1234567'
    token.provider = 'test_provider'
    token.data = {'avatar_url': 'avatar2.png'}
    user.tokens.append(token)
    DBSession.add(user)
    users.append(user)

    def finalizer():
        pass
        #for user in users:
        #    DBSession.delete(tag)
        #commit()
    #request.addfinalizer(finalizer)

    commit()
    return users
