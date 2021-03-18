FROM python:3.8-alpine as base

RUN apk --no-cache add \
    nano \
    less \
    make \
    git \
    python3-dev libffi-dev gcc g++ musl-dev \
&& true
RUN pip3 install --no-cache-dir --upgrade pip setuptools virtualenv

EXPOSE 6543
EXPOSE 9873
VOLUME /logs
HEALTHCHECK --interval=1m --timeout=3s CMD wget -q http://127.0.0.1:6543/ -O /dev/null

# copy just requirements.txt by itself, so that we only re-run this
# step when this file changes, not when *anything* changes
WORKDIR /app
RUN virtualenv data/_env
COPY requirements.txt /tmp/requirements.txt
RUN data/_env/bin/pip3 install --no-cache-dir -r /tmp/requirements.txt

COPY . /app
RUN make install
CMD make run_production


FROM base as test
RUN make test


FROM base
