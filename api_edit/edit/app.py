import logging
import textwrap
from pathlib import Path
from typing import Generator

import litestar
from litestar.config.response_cache import CACHE_FOREVER
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import RedocRenderPlugin

from .config import AppConfig, init_config_from_env
from .responses import FilesResponse

logger = logging.getLogger(__name__)


@litestar.get(
    path="/favicon.ico",
    tags=("Public",),
    summary="favicon",
    description=textwrap.dedent("""Suppress the errors"""),
    cache=CACHE_FOREVER,
    cache_control=litestar.datastructures.CacheControlHeader(max_age=360, public=True),
)
async def favicon(config: AppConfig) -> str:
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
async def files(config: AppConfig) -> FilesResponse:
    def _text_files(path: Path) -> Generator[Path]:
        for root, dirs, files in path.walk(follow_symlinks=False):
            for file_str in files:
                file = root.joinpath(file_str)
                if file.suffix not in (".txt", ".str"):
                    continue
                yield file.relative_to(path)
    return tuple(_text_files(config.path_source))


def init_config(app: litestar.Litestar) -> None:
    app.state.config = init_config_from_env(debug=app.debug)


async def provide_config(request: litestar.Request) -> AppConfig:
    return request.app.state.config


def create_app() -> litestar.Litestar:
    app = litestar.Litestar(
        route_handlers=(favicon, files),
        on_startup=(init_config,),
        dependencies={"config": litestar.di.Provide(provide_config)},
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
