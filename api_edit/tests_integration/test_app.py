import json
import urllib.request
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import MappingProxyType
from typing import AsyncGenerator

# import aiohttp
import pytest

# ------------------------------------------------------------------------------

# Trying to do async http requests seems impossible due to multiple event loops
# Degrading to plain blocking python until I can come up with a better plan

type JsonPrimitives = str | int | float | bool | None
type JsonObject = Mapping[str, Json | JsonPrimitives]
type JsonSequence = Sequence[Json | JsonPrimitives]
type Json = JsonObject | JsonSequence


def request(
    url: str,
    method: str = "GET",
    headers: Mapping[str, str] = MappingProxyType({}),
    data: bytes | None = None,
) -> bytes:
    request = urllib.request.Request(url=url, method=method, data=data, headers=headers)  # type: ignore
    with urllib.request.urlopen(request) as f:
        return f.read()


def request_json(
    url, method="GET", headers: Mapping[str, str] = MappingProxyType({}), data=None
) -> Json:
    headers = {"content-type": "text/javascript"} | headers  # type: ignore
    return json.loads(request(url, method, headers, data))


# ------------------------------------------------------------------------------


class EditService:
    def __init__(
        self,
        # client: aiohttp.ClientSession,
        EDIT_ENDPOINT: str,
        PATH_SOURCE: Path,
    ):
        # self.client = client
        self.EDIT_ENDPOINT = EDIT_ENDPOINT
        self.PATH_SOURCE = PATH_SOURCE
        self.tempfile_prefix = "_api_edit.pytest"

    def _create_tempfiles(self) -> None:
        txt = self.PATH_SOURCE.joinpath(self.tempfile_prefix + ".txt")
        srt = self.PATH_SOURCE.joinpath(self.tempfile_prefix + ".srt")
        txt.write_text("fake tags")
        srt.write_text("fake srt")

    def _teardown_tempfiles(self) -> None:
        for file in self.PATH_SOURCE.iterdir():
            if file.name.startswith(self.tempfile_prefix):
                file.unlink()

    @property
    async def index(self) -> str:
        # return await (await self.client.get(self.EDIT_ENDPOINT + "/")).text()
        return request(self.EDIT_ENDPOINT + "/").decode("utf8")

    @property
    async def files(self) -> Sequence[str]:
        # return await (await self.client.get(self.EDIT_ENDPOINT + "/files.json")).json()
        return request_json(self.EDIT_ENDPOINT + "/files.json")  # type: ignore

    def get_file(self, filename: str) -> str:
        return request(self.EDIT_ENDPOINT + "/file/" + filename.strip("/")).decode(
            "utf8"
        )

    def post_file(self, filename: str, **contents: str) -> None:
        request(
            self.EDIT_ENDPOINT + "/file/" + filename.strip("/"),
            method="POST",
            data=json.dumps(contents).encode(),
        )

    def file_history(self, filename: str) -> Sequence[str]:
        """
        Old version of the file are kept in files with a new suffix
        """
        return tuple(f.read_text() for f in self.PATH_SOURCE.glob(filename + "*"))


@pytest.fixture(scope="session")
async def edit_service(
    # client: aiohttp.ClientSession,
    EDIT_ENDPOINT: str,
    PATH_SOURCE: Path,
) -> AsyncGenerator[EditService]:
    edit_service = EditService(EDIT_ENDPOINT, PATH_SOURCE)
    edit_service._create_tempfiles()
    yield edit_service
    edit_service._teardown_tempfiles()


async def test_index(edit_service: EditService) -> None:
    index = await edit_service.index
    assert "<html>" in index


async def test_files(edit_service: EditService) -> None:
    files = await edit_service.files
    files = [f for f in files if f.startswith(edit_service.tempfile_prefix)]
    assert files


async def test_file_get(edit_service: EditService) -> None:
    assert edit_service.get_file(edit_service.tempfile_prefix + ".txt")
    assert edit_service.get_file(edit_service.tempfile_prefix + ".srt")


async def test_file_post(edit_service: EditService) -> None:
    filename = edit_service.tempfile_prefix + ".txt"

    old_content = edit_service.get_file(filename)

    edit_service.post_file(filename, content="New content")
    new_content = edit_service.get_file(filename)
    assert old_content != new_content
    assert new_content == "New content"

    assert frozenset(edit_service.file_history(filename)) >= frozenset(
        (old_content, new_content)
    )
