FROM python:slim as base
    WORKDIR /app/

FROM base as python_dependencies
    COPY ./requirements.txt ./
    RUN pip install --no-cache-dir -r requirements.txt -t /site-packages
    ENV PYTHONPATH=/site-packages
FROM python_dependencies as python_dependencies_test
    COPY ./requirements.test.txt ./
    RUN pip install --no-cache-dir -r requirements.test.txt -t /site-packages

FROM python_dependencies as code
    COPY ./api_queue ./api_queue

FROM code as test
    COPY --from=python_dependencies_test /site-packages /site-packages
    CMD ["python", "-m", "api_queue.server"]

    COPY ./tests ./tests
    COPY ./pytest.ini ./
    RUN python3 -m pytest -x

    COPY ./.mypy.ini ./
    RUN python3 -m mypy api_queue


FROM code as production
    EXPOSE 8000
    CMD ["python", "-m", "sanic", "api_queue.server.app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
