ARG PYTHON_IMAGE_VERSION=3.10
FROM python:${PYTHON_IMAGE_VERSION}-alpine as base
    ARG PYTHON_IMAGE_VERSION
    ENV PATH_SITE_PACKAGES=/usr/local/lib/python${PYTHON_IMAGE_VERSION}/site-packages/

    WORKDIR /app/
    EXPOSE 1337

    RUN apk add --no-cache \
        curl \
    && true

FROM base as python_dependencies
    COPY ./requirements.txt ./
    RUN apk add --no-cache --virtual .build-deps \
            build-base \
            libffi-dev \
        && pip install -U setuptools pip \
        && pip install --no-cache-dir -r requirements.txt \
    && apk --purge del .build-deps
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
    #RUN pytest -x
    CMD ["python", "-m", "api_queue.server"]

FROM code as production
    CMD ["python", "-m", "sanic", "api_queue.server.app", "--host", "0.0.0.0", "--port", "1337", "--workers", "4"]
    HEALTHCHECK --interval=1m --timeout=3s CMD curl --fail http://127.0.0.1:1337/ || exit 1
