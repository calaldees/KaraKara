FROM docker.io:latest

RUN apt-get update && apt-get install -y \
    python3-pip \
&& apt-get clean && rm -rf /var/lib/apt/lists /var/cache/apt
RUN pip3 install --upgrade pip setuptools virtualenv

COPY processmedia2.pip requirements.pip
RUN pip3 install -r requirements.pip

WORKDIR /processmedia2
CMD ["make", "run"]

# docker build -t processmedia2:latest --file .\processmedia2.dockerfile .
# docker run -it --rm -v ../:/processmedia2:ro -v /var/run/docker.sock:/var/run/docker.sock docker.io processmedia2:latest
