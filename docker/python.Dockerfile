FROM python:3
RUN pip3 install --upgrade pip setuptools virtualenv
RUN apt-get update && apt-get install -y \
    nano \
    curl \
    less \
 && apt-get clean && rm -rf /var/lib/apt/lists /var/cache/apt
