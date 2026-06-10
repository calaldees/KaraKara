import os
from pathlib import Path

import pytest

HTTP_TIMEOUT = int(os.environ.get("HTTP_REQUEST_TIMEOUT", "1"))
_EDIT_ENDPOINT = os.environ.get("EDIT_ENDPOINT", "http://localhost:8000")
_PATH_SOURCE = os.environ.get("PATH_SOURCE", "../media/source")


@pytest.fixture(scope="session")
def EDIT_ENDPOINT() -> str:
    return _EDIT_ENDPOINT


@pytest.fixture(scope="session")
def PATH_SOURCE() -> Path:
    path_source = Path(_PATH_SOURCE)
    assert path_source.is_dir()
    return path_source


# @pytest.fixture(scope="session")
# async def client() -> AsyncGenerator[aiohttp.ClientSession]:
# async with aiohttp.ClientSession(
# 1timeout=aiohttp.ClientTimeout(total=HTTP_TIMEOUT),
# ) as client:
#    yield client
