FROM python:3.13-alpine AS base

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir .

RUN mkdir -p /uploads

EXPOSE 8000

FROM python:3.13-alpine AS base
    WORKDIR /app/
    RUN apk add --no-cache \
        bash \
    && true

FROM base AS python_dependencies
    COPY ./pyproject.toml ./
    RUN pip install --no-cache-dir -e . -t /site-packages
    ENV PYTHONPATH=/site-packages

FROM python_dependencies AS code
    COPY ./*.html ./
    COPY ./*.py ./

FROM code AS production
    EXPOSE 8000
    #CMD ["python", "-m", "sanic", "api_queue.server.app", "--host", "0.0.0.0", "--port", "8000", "--single-process"]
	CMD ["python", "-m", "sanic", "upload:app", "--host=0.0.0.0", "--port=8000", "--access-log", "--single-process"]
