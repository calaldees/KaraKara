ARG FFMPEG_VERSION=latest
ARG PYTHON_VERSION=
#ARG FFMPEG_VERSION=5.1.2
#ARG PYTHON_VERSION=3.11-

# Can't use ARG variables in `COPY --from`, but can use them in `FROM`...
FROM mwader/static-ffmpeg:${FFMPEG_VERSION} as ffmpeg

FROM python:${PYTHON_VERSION}alpine as dependencies
    WORKDIR /app/
    VOLUME /logs
    VOLUME /media/source
    VOLUME /media/processed

    RUN apk add --no-cache \
        imagemagick

    COPY ./pyproject.toml ./
    RUN pip install --no-cache-dir -e . -t /site-packages
    ENV PYTHONPATH=/site-packages

    COPY --from=ffmpeg /ffmpeg /usr/local/bin/
    COPY --from=ffmpeg /ffprobe /usr/local/bin/

FROM dependencies as dependencies_test
    RUN pip install --no-cache-dir -e '.[test]' -t /site-packages

FROM dependencies as code
    COPY main.py .
    COPY lib ./lib
    COPY logging.config.json .

FROM code as test
    COPY --from=dependencies_test /site-packages /site-packages
    COPY tests ./tests
    RUN python3 -m mypy .
    RUN python3 -m pytest

FROM code as production
    ENTRYPOINT ["python3", "main.py", "--source", "/media/source", "--cache", "/media/processed/cache.db", "--processed", "/media/processed"]
    CMD ["all", "--loop", "600"]
