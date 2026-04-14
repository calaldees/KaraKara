import pathlib
from collections.abc import AsyncIterator, Generator, Sequence

import litestar
import litestar.testing
import pytest

from edit.model import FileModel


@pytest.fixture
def app() -> Generator[litestar.Litestar]:
    from edit.app import create_app

    app = create_app()
    app.debug = True
    yield app


@pytest.fixture
def route_handlers() -> Sequence[litestar.types.ControllerRouterHandler]:
    from edit.app import file_read, file_write, files, index

    return (index, files, file_read, file_write)


async def provide_file_model() -> FileModel:
    return FileModel(path_source=pathlib.Path())


@pytest.fixture
async def client(
    route_handlers: Sequence[litestar.types.ControllerRouterHandler],
) -> AsyncIterator[litestar.testing.AsyncTestClient[litestar.Litestar]]:
    async with litestar.testing.create_async_test_client(
        route_handlers=route_handlers,
        dependencies={
            "file_model": litestar.di.Provide(provide_file_model),
        },
    ) as client:
        yield client
