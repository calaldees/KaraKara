FROM python:3.13-alpine AS base
WORKDIR /app
RUN apk add --no-cache bash
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    pip install -e '.[analytics]'
COPY ./api_queue ./api_queue
COPY ./*.py ./

FROM base AS test
COPY pyproject.toml ./
COPY ./tests ./tests
RUN pytest
RUN mypy .

FROM base AS production
VOLUME /logs
VOLUME /queues
VOLUME /media/processed
EXPOSE 8000
CMD ["python", "-m", "sanic", "api_queue.server.app", "--host", "0.0.0.0", "--port", "8000", "--single-process"]
# "--workers", "4"  # workers are python.multithreading rather than async. For now, we can just stick with single process
