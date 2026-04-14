import dataclasses
import logging
import os
import textwrap
from collections.abc import Iterable
from pathlib import Path

import litestar
from litestar.config.response_cache import CACHE_FOREVER
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import RedocRenderPlugin

from .model import FileModel

logger = logging.getLogger(__name__)

INDEX = Path(__file__).parent.joinpath("index.html").read_text()


@litestar.get(
    path="/",
    tags=("Public",),
    summary="Mini HTML frontend",
    description=textwrap.dedent("""
        Renders `index.html`
    """),
    media_type=litestar.MediaType.HTML,
    cache=CACHE_FOREVER,
    cache_control=litestar.datastructures.CacheControlHeader(max_age=360, public=True),
)
async def index() -> str:
    return INDEX


@litestar.get(
    path="/files.json",
    tags=("Public",),
    summary="files",
    description=textwrap.dedent("""
    """),
    # cache=, TODO
    cache_control=litestar.datastructures.CacheControlHeader(max_age=360, public=True),
)
async def files(file_model: FileModel) -> Iterable[Path]:
    return file_model.files


@litestar.get(
    path="/file/{file_path:path}",
    tags=("Public",),
    summary="Single File Contents",
    description=textwrap.dedent("""
    """),
    media_type=litestar.MediaType.TEXT,
)
async def file_read(file_model: FileModel, file_path: str) -> str:
    return file_model.file_read(Path(file_path.lstrip("/")))


@dataclasses.dataclass
class FileContents:
    content: str


@litestar.post(
    path="/file/{file_path:path}",
    tags=("Public",),
    summary="Save File Contents",
    description=textwrap.dedent("""
    """),
)
async def file_write(file_model: FileModel, file_path: str, data: FileContents) -> None:
    file_model.file_write(Path(file_path.lstrip("/")), data.content)


def init_file_model(app: litestar.Litestar) -> None:
    path_source = Path(os.getenv("PATH_HOST_media", "")).joinpath("source")
    app.state.file_model = FileModel(path_source)


async def provide_file_model(request: litestar.Request) -> FileModel:
    return request.app.state.file_model


def create_app() -> litestar.Litestar:
    app = litestar.Litestar(
        route_handlers=(index, files, file_read, file_write),
        on_startup=(init_file_model,),
        dependencies={"file_model": litestar.di.Provide(provide_file_model)},
        openapi_config=OpenAPIConfig(
            title="Edit Service",
            version="0.0.0",
            description=textwrap.dedent("""
            """),
            tags=[],
            path="/_docs",
            render_plugins=(RedocRenderPlugin(),),
        ),
    )
    return app
