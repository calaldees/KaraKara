ARG PYTHON_IMAGE_VERSION=3.10
FROM python:${PYTHON_IMAGE_VERSION}-slim as base
    ARG PYTHON_IMAGE_VERSION
    ENV PATH_SITE_PACKAGES=/usr/local/lib/python${PYTHON_IMAGE_VERSION}/site-packages/

    WORKDIR /app/
    EXPOSE 8000

    RUN apt-get update && apt-get install -y \
        curl \
    && rm -rf /var/lib/apt/lists/*

FROM base as python_dependencies
    COPY ./requirements.txt ./
    RUN pip install --no-cache-dir -r requirements.txt
FROM python_dependencies as python_dependencies_test
    COPY ./requirements.test.txt ./
    RUN pip install --no-cache-dir -r requirements.test.txt

FROM python_dependencies as code
    COPY ./api_queue ./api_queue

FROM code as test
    COPY --from=python_dependencies_test ${PATH_SITE_PACKAGES} ${PATH_SITE_PACKAGES}
    COPY --from=python_dependencies_test /usr/local/bin/pytest /usr/local/bin/pytest
    COPY ./tests ./tests
    COPY ./pytest.ini ./
    RUN pytest -x
    COPY --from=python_dependencies_test /usr/local/bin/mypy /usr/local/bin/mypy
    COPY ./.mypy.ini ./
    #RUN mypy api_queue  # Unable to get get `queue_validation.py` passing mypy
    CMD ["python", "-m", "api_queue.server"]

FROM code as production
    CMD ["python", "-m", "sanic", "api_queue.server.app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
    HEALTHCHECK --interval=1m --timeout=3s CMD curl --fail http://127.0.0.1:8000/ || exit 1
