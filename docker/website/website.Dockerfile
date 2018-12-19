FROM python:3-alpine

# Upgrade python tools
RUN pip3 install --no-cache-dir --upgrade pip setuptools virtualenv

#RUN apt-get update && apt-get install -y \
RUN apk --no-cache add \
    nano \
    curl \
    less \
    make \
    git \
&& true
#&& apt-get clean && rm -rf /var/lib/apt/lists /var/cache/apt
