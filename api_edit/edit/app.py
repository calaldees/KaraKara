import dataclasses
import pathlib
import textwrap
from typing import Annotated

import litestar
from litestar.config.response_cache import CACHE_FOREVER
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import RedocRenderPlugin


README = pathlib.Path(__file__).parent.joinpath('README.md').read_text()


@litestar.get(
    path='/',
    tags=('Public',),
    summary='Default Root',
    description=textwrap.dedent("""
        Basic information about the service
        Renders `README.md`
    """),
    cache=CACHE_FOREVER,
    cache_control=litestar.datastructures.CacheControlHeader(max_age=360, public=True),
)
async def root() -> str:
    return README


def create_app() -> litestar.Litestar:
    app = litestar.Litestar(
        route_handlers=(
            root,
        ),
        openapi_config=OpenAPIConfig(
            title='Edit Service',
            version='0.0.0',
            description=textwrap.dedent("""
            """),
            tags=[],
            path='/_docs',
            render_plugins=(RedocRenderPlugin(),),
        ),
    )
    return app
