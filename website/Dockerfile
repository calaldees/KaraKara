FROM python:3-alpine

# Upgrade python tools
RUN pip3 install --no-cache-dir --upgrade pip setuptools virtualenv

RUN apk --no-cache add \
    nano \
    curl \
    less \
    make \
    git \
&& true

# http, websocket
EXPOSE 6543
EXPOSE 9873

# copy just this file by itself, so that we only re-run this
# step when this file changes, not when *anything* changes
WORKDIR /app
RUN virtualenv data/_env
COPY requirements.pip /tmp/requirements.pip
RUN /app/data/_env/bin/pip3 install -r /tmp/requirements.pip

COPY . /app
RUN make install
CMD make run_production
