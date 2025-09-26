FROM python:3.13-alpine AS base
    WORKDIR /app/
    RUN apk add --no-cache \
        bash \
    && true

FROM base AS python_dependencies
    COPY ./pyproject.toml ./
    RUN pip install --no-cache-dir -e . -t /site-packages
    ENV PYTHONPATH=/site-packages
FROM python_dependencies AS python_dependencies_test
    RUN pip install --no-cache-dir -e '.[test]' -t /site-packages

FROM python_dependencies AS code
    COPY ./api_queue ./api_queue
    COPY ./*.py ./

FROM code AS test
    COPY --from=python_dependencies_test /site-packages /site-packages
    COPY ./tests ./tests
    RUN python3 -m pytest -x
    RUN python3 -m mypy .
    CMD ["python", "-m", "api_queue.server"]

FROM code AS production
    EXPOSE 8000
    CMD ["python", "-m", "sanic", "api_queue.server.app", "--host", "0.0.0.0", "--port", "8000", "--single-process"]
    # "--workers", "4"  # workers are python.multithreading rather than async. For now, we can just stick with single process
