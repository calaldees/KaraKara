FROM python:3.14-alpine AS base
WORKDIR /app
COPY --from=mwader/static-ffmpeg:7.1.1 /ffmpeg /ffprobe /usr/local/bin/
RUN apk add --no-cache \
    imagemagick imagemagick-jpeg imagemagick-webp imagemagick-heic
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    pip install -e .
COPY ./pm3 ./pm3

FROM base AS test
COPY pyproject.toml ./
RUN pip install --group dev -e .
COPY tests ./tests
RUN pytest
RUN mypy .

FROM base AS production
ENV TZ=Etc/UTC
VOLUME /media/source
VOLUME /media/processed
ENTRYPOINT [ "python3", "-m", "pm3", "--source", "/media/source", "--processed", "/media/processed" ]
CMD ["all", "--loop", "600"]
