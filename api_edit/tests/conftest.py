from collections.abc import AsyncIterator, Generator, Sequence

import litestar
import litestar.testing
import pytest


@pytest.fixture
def app() -> Generator[litestar.Litestar]:
    from edit.app import create_app

    app = create_app()
    app.debug = True
    yield app


@pytest.fixture
def route_handlers() -> Sequence[litestar.types.ControllerRouterHandler]:
    from edit.app import (
        root,
    )

    return (
        root,
    )



@pytest.fixture
async def client(
    route_handlers: Sequence[litestar.types.ControllerRouterHandler],
) -> AsyncIterator[litestar.testing.AsyncTestClient[litestar.Litestar]]:
    async with litestar.testing.create_async_test_client(
        route_handlers=route_handlers,
        dependencies={
        },
    ) as client:
        yield client
