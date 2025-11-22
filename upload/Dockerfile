FROM python:3.14-alpine AS base

VOLUME /uploads
WORKDIR /app
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    pip install --no-cache-dir .

COPY . /app
EXPOSE 8000
CMD ["uvicorn", "upload:app", "--host", "0.0.0.0", "--port", "8000"]
