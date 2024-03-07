ARG FFMPEG_VERSION=5.1.2

# Can't use ARG variables in `COPY --from`, but can use them in `FROM`...
FROM mwader/static-ffmpeg:${FFMPEG_VERSION} as ffmpeg

FROM python:3.11-alpine as dependencies
    WORKDIR /app/
    RUN apk add --no-cache \
        imagemagick
    COPY ./requirements.txt ./
    RUN pip install --no-cache-dir -r requirements.txt -t /site-packages
    ENV PYTHONPATH=/site-packages
    COPY --from=ffmpeg /ffmpeg /usr/local/bin/
    COPY --from=ffmpeg /ffprobe /usr/local/bin/
FROM dependencies as dependencies_test
    COPY ./requirements.test.txt ./
    RUN pip install --no-cache-dir -r requirements.test.txt -t /site-packages

FROM dependencies as code
    COPY main.py .
    COPY lib ./lib
    VOLUME /logs
    VOLUME /media/source
    VOLUME /media/processed

FROM code as test
    COPY --from=dependencies_test /site-packages /site-packages
    COPY .mypy.ini .
    COPY tests ./tests
    RUN python3 -m mypy .
    RUN python3 -m tests.test_main

FROM code as production
    ENTRYPOINT ["python3", "/app/main.py", "--source", "/media/source", "--cache", "/media/processed/cache.db", "--processed", "/media/processed"]
    CMD ["all", "--loop", "600"]
