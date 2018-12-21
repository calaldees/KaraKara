FROM ubuntu:latest
VOLUME /logs
VOLUME /media/source
VOLUME /media/meta
VOLUME /media/processed

# It is possible that encoding could really take more than 30 mins
# HEALTHCHECK --interval=1m --timeout=3s CMD touch -d"-30min" /tmp/marker && [ /processmedia2/.heartbeat -nt /tmp/marker ]

COPY --from=jrottenberg/ffmpeg /usr/local /usr/local

RUN apt-get update && apt-get install -y \
    git \
    python3-pip \
    jpegoptim \
    tesseract-ocr-eng \
    sox \
&& apt-get clean && rm -rf /var/lib/apt/lists /var/cache/apt
RUN pip3 install --upgrade pip setuptools

COPY processmedia2.pip requirements.pip
RUN pip3 install -r requirements.pip

WORKDIR /processmedia2

COPY ./ ./
CMD ./processmedia2.sh



#RUN mkdir -p /media/source /media/meta /media/processed && chmod -R 777 /media/

#COPY --from=krallin/ubuntu-tini /usr/local/bin/tini /usr/local/bin/tini
#ENTRYPOINT ["/usr/local/bin/tini", "--", "/processmedia2/docker-compose.yml.processmedia2.sh"]
#https://github.com/docker-library/mysql/issues/47#issuecomment-140339288
#CMD /processmedia2/processmedia2.sh

# docker build -t processmedia2:latest --file .\processmedia2.base.dockerfile .
# docker run -it --rm -v ../:/processmedia2:ro -v /var/run/docker.sock:/var/run/docker.sock docker.io processmedia2:latest
  # Windows -v //var/run/docker.sock:/var/run/docker.sock
