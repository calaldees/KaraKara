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

type FilesResponse = Iterable[Path]
type FileContentResponse = str


@litestar.get(
    path="/favicon.ico",
    tags=("Public",),
    summary="favicon",
    description=textwrap.dedent("""Suppress the errors"""),
    cache=CACHE_FOREVER,
    cache_control=litestar.datastructures.CacheControlHeader(max_age=360, public=True),
)
async def favicon() -> str:
    return ""


@litestar.get(
    path="/",
    tags=("Public",),
    summary="files",
    description=textwrap.dedent("""
    """),
    # cache=, TODO
    cache_control=litestar.datastructures.CacheControlHeader(max_age=360, public=True),
)
async def files(file_model: FileModel) -> FilesResponse:
    return file_model.files


@litestar.get(
    path="/file/{file_path:str}",
    tags=("Public",),
    summary="Single File Contents",
    description=textwrap.dedent("""
    """),
    media_type=litestar.MediaType.TEXT,
)
async def file_read(file_model: FileModel, file_path: str) -> FileContentResponse:
    return file_model.file_read(Path(file_path))


@litestar.post(
    path="/file/{file_path:str}",
    tags=("Public",),
    summary="Save File Contents",
    description=textwrap.dedent("""
    """),
)
async def file_write(file_model: FileModel, file_path: str, data: str) -> None:
    file_model.file_write(Path(file_path), data)


def init_file_model(app: litestar.Litestar) -> None:
    path_source = Path(os.getenv("PATH_HOST_media", "")).joinpath("source")
    app.state.file_model = FileModel(path_source)


async def provide_file_model(request: litestar.Request) -> FileModel:
    return request.app.state.file_model


def create_app() -> litestar.Litestar:
    app = litestar.Litestar(
        route_handlers=(favicon, files, file_read, file_write),
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
