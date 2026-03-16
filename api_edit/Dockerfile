FROM astral/uv:python3.14-alpine AS base

    # https://docs.astral.sh/ruff/configuration/#full-command-line-interface
    # https://mypy.readthedocs.io/en/stable/config_file.html#confval-cache_dir
    ENV RUFF_CACHE_DIR=/.ruff_cache
    ENV MYPY_CACHE_DIR=/.mypy_cache
    ENV UV_PROJECT_ENVIRONMENT=/.uv.venv
    ENV UV_NO_SYNC=True
    ENV LITESTAR_PORT=8000
    ENV LITESTAR_HOST=0.0.0.0

    WORKDIR /app/

FROM base AS dependencies
    COPY pyproject.toml uv.lock ./
    RUN UV_NO_SYNC=False uv sync --no-dev
FROM dependencies AS test_dependencies
    RUN UV_NO_SYNC=False uv sync

FROM dependencies AS code
    COPY . .

FROM test_dependencies AS test
    COPY --from=code /app .
    CMD [ "uv", "run", "litestar", "run" ]
FROM code AS production
    CMD [ "uv", "run", "litestar", "run" ]
