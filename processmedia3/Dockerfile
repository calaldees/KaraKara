ARG FFMPEG_VERSION=7.1.1
ARG PYTHON_VERSION=3.14

# Can't use ARG variables in `COPY --from`, but can use them in `FROM`...
FROM mwader/static-ffmpeg:${FFMPEG_VERSION} AS ffmpeg

FROM python:${PYTHON_VERSION}-alpine AS dependencies
WORKDIR /app/
VOLUME /logs
VOLUME /media/source
VOLUME /media/processed

RUN apk add --no-cache \
    imagemagick imagemagick-jpeg imagemagick-webp imagemagick-heic

COPY ./pyproject.toml ./
RUN pip install --no-cache-dir -e . -t /site-packages
ENV PYTHONPATH=/site-packages

COPY --from=ffmpeg /ffmpeg /usr/local/bin/
COPY --from=ffmpeg /ffprobe /usr/local/bin/

FROM dependencies AS dependencies_test
RUN pip install --no-cache-dir -e '.[test]' -t /site-packages

FROM dependencies AS code
COPY main.py .
COPY lib ./lib

FROM code AS test
COPY --from=dependencies_test /site-packages /site-packages
COPY tests ./tests
RUN python3 -m mypy .
RUN python3 -m pytest

FROM code AS production
ENTRYPOINT [ "python3", "main.py", "--source", "/media/source", "--processed", "/media/processed", "--log-file", "/logs/processmedia3.log" ]
CMD ["all", "--loop", "600"]
