FROM python:3.14-alpine AS base
WORKDIR /app
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    pip install --no-cache-dir --group dev .
COPY . /app

FROM base AS test
RUN pytest
RUN mypy .

FROM base AS production
EXPOSE 8000
VOLUME /logs
VOLUME /uploads
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
