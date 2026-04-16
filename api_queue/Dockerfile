FROM astral/uv:python3.14-alpine AS base
    # https://docs.astral.sh/ruff/configuration/#full-command-line-interface
    # https://mypy.readthedocs.io/en/stable/config_file.html#confval-cache_dir
    ENV RUFF_CACHE_DIR=/.ruff_cache
    ENV MYPY_CACHE_DIR=/.mypy_cache
    ENV UV_PROJECT_ENVIRONMENT=/.uv.venv
    ENV UV_NO_SYNC=True

    WORKDIR /app/

FROM base AS dependencies
    COPY pyproject.toml uv.lock ./
    RUN UV_NO_SYNC=False uv sync --no-dev
FROM dependencies AS test_dependencies
    RUN UV_NO_SYNC=False uv sync --all-extras

FROM dependencies AS code
    COPY ./api_queue ./api_queue
    COPY ./*.py ./

FROM test_dependencies AS test
    COPY --from=code /app .
    COPY ./tests .
    # Both pytest and mypy fail
    # Running pytest as part of docker:`RUN` is somehow broken?
    # https://community.sanicframework.org/t/sanic-app-name-xxx-already-in-use-while-running-in-docker/1106/5
    # Suggest moving away from sanic to litestar. Untangle the app logic from the framework by using a domain model.
    #RUN uv run pytest
    #RUN uv run mypy .

FROM code AS production
    VOLUME /logs
    VOLUME /queues
    VOLUME /media/processed
    EXPOSE 8000
    CMD ["uv", "run", "sanic", "api_queue.server.app", "--host", "0.0.0.0", "--port", "8000", "--single-process"]
