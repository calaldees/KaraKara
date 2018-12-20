FROM python:3.7

# http, websocket
EXPOSE 6543
EXPOSE 9873

RUN apt-get update && apt-get install -y \
    nano \
    curl \
    less \
 && apt-get clean && rm -rf /var/lib/apt/lists /var/cache/apt
RUN pip3 install --upgrade pip setuptools virtualenv

# copy just this file by itself, so that we only re-run this
# step when this file changes, not when *anything* changes
WORKDIR /app
RUN virtualenv data/_env
COPY requirements.pip /tmp/requirements.pip
RUN data/_env/bin/pip3 install -r /tmp/requirements.pip

COPY . /app
RUN make install
CMD make run_production
