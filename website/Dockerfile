FROM python:3-alpine
EXPOSE 6543
EXPOSE 9873
VOLUME /logs
HEALTHCHECK --interval=1m --timeout=3s CMD curl --fail http://127.0.0.1:6543/ || exit 1

# Upgrade python tools
RUN pip3 install --no-cache-dir --upgrade pip setuptools virtualenv

RUN apk --no-cache add \
    nano \
    curl \
    less \
    make \
    git \
&& true

# copy just this file by itself, so that we only re-run this
# step when this file changes, not when *anything* changes
WORKDIR /app
RUN virtualenv data/_env
COPY requirements.pip /tmp/requirements.pip
RUN data/_env/bin/pip3 install -r /tmp/requirements.pip

COPY . /app
RUN make install
CMD make run_production
