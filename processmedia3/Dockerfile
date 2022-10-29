FROM python:3.10 as tests
RUN apt install -y imagemagick
COPY --from=mwader/static-ffmpeg /ffmpeg /usr/local/bin/
COPY --from=mwader/static-ffmpeg /ffprobe /usr/local/bin/
RUN pip install tqdm TestSlide mypy black
COPY main.py .mypy.ini /app/
COPY lib /app/lib/
COPY tests /app/tests/
WORKDIR /app
RUN mypy main.py
RUN testslide tests/test_main.py

FROM python:3.10-alpine as base

VOLUME /logs
VOLUME /media/source
VOLUME /media/meta
VOLUME /media/processed

RUN apk add imagemagick
COPY --from=mwader/static-ffmpeg /ffmpeg /usr/local/bin/
COPY --from=mwader/static-ffmpeg /ffprobe /usr/local/bin/

RUN pip install tqdm
COPY main.py /app/
COPY lib /app/lib/

CMD python3 /app/main.py \
  --source /media/source \
  --cache /media/meta/cache.db \
  --processed /media/processed \
  --loop 600 \
  | tee /logs/processmedia3.log
