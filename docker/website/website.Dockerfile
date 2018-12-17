FROM python:3-alpine

#RUN apt-get update && apt-get install -y \
RUN apk --update --no-cache add \
    nano \
    curl \
    less \
    make \
    git \
&& rm -rf /var/lib/apt/lists/* && rm -rf /var/cache/apk/*
#&& apt-get clean && rm -rf /var/lib/apt/lists /var/cache/apt

RUN pip3 install --no-cache-dir --upgrade pip setuptools virtualenv
