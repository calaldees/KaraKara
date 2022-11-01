ARG FFMPEG_VERSION=5.1.2

# Can't use ARG variables in `COPY --from`, but can use them in `FROM`...
FROM mwader/static-ffmpeg:${FFMPEG_VERSION} as ffmpeg

FROM python:3.11 as test
    RUN apt install -y imagemagick
    COPY --from=ffmpeg /ffmpeg /usr/local/bin/
    COPY --from=ffmpeg /ffprobe /usr/local/bin/
    RUN pip install tqdm mypy
    COPY main.py .mypy.ini /app/
    COPY lib /app/lib/
    COPY tests /app/tests/
    WORKDIR /app
    RUN mypy main.py
    RUN python3 -m tests.test_main

FROM python:3.11-alpine as production
    VOLUME /logs
    VOLUME /media/source
    VOLUME /media/processed

    RUN apk add imagemagick
    COPY --from=ffmpeg /ffmpeg /usr/local/bin/
    COPY --from=ffmpeg /ffprobe /usr/local/bin/

    RUN pip install tqdm
    COPY main.py /app/
    COPY lib /app/lib/

    ENTRYPOINT ["python3", "/app/main.py", "--source", "/media/source", "--cache", "/media/processed/cache.db", "--processed", "/media/processed"]
    CMD ["all", "--loop", "600"]
