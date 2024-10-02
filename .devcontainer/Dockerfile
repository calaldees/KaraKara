ARG FFMPEG_VERSION=7.0
FROM mwader/static-ffmpeg:${FFMPEG_VERSION} as ffmpeg

FROM debian:stable-slim
RUN mkdir /logs
COPY --from=ffmpeg /ffmpeg /usr/local/bin/
COPY --from=ffmpeg /ffprobe /usr/local/bin/
RUN apt update && apt install -y python3 python3-venv npm curl imagemagick
