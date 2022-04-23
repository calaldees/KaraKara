import pytest

@pytest.fixture
def app():
    from api_queue.server import app

    # get the single registered app - is this needed? can we just import app from server?
    #from sanic import Sanic
    #app = Sanic.get_app()

    return app
