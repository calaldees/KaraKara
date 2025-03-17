FROM python:3.13-alpine as base
    WORKDIR /app/
    RUN apk add --no-cache \
        bash \
    && true

FROM base as python_dependencies
    COPY ./pyproject.toml ./
    RUN pip install --no-cache-dir -e . -t /site-packages
    ENV PYTHONPATH=/site-packages
FROM python_dependencies as python_dependencies_test
    RUN pip install --no-cache-dir -e '.[test]' -t /site-packages

FROM python_dependencies as code
    COPY ./api_queue ./api_queue

FROM code as test
    COPY --from=python_dependencies_test /site-packages /site-packages
    CMD ["python", "-m", "api_queue.server"]

    COPY ./tests ./tests
    RUN python3 -m pytest -x
    RUN python3 -m mypy api_queue

FROM code as production
    EXPOSE 8000
    CMD ["python", "-m", "sanic", "api_queue.server.app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
