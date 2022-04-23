import pytest

# https://sanic.dev/en/plugins/sanic-testing/getting-started.html#basic-usage
@pytest.mark.asyncio
async def test_basic_asgi_client(app):
    request, response = await app.asgi_client.get("/")

    assert request.method.lower() == "get"
    assert response.body == b"foo"
    assert response.status == 200
