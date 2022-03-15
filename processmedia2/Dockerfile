ARG PYTHON_IMAGE_VERSION=3.10
FROM python:${PYTHON_IMAGE_VERSION}-alpine as base
    ARG PYTHON_IMAGE_VERSION
    ENV PATH_SITE_PACKAGES=/usr/local/lib/python${PYTHON_IMAGE_VERSION}/site-packages/
#FROM ubuntu as base
    #ENV PATH_SITE_PACKAGES=/usr/local/lib/python3.8/dist-packages/

    # System Dependencies ------------------------------------------------------

    # old ubuntu
    # COPY --from=jrottenberg/ffmpeg /usr/local /usr/local
    # ENV DEBIAN_FRONTEND=noninteractive
    # ENV TZ=Etc/UTC
    # RUN apt-get update && apt-get install -y \
    #     git \
    #     python3-pip \
    #     jpegoptim \
    #     sox \
    #     tesseract-ocr-eng \
    # && apt-get clean && rm -rf /var/lib/apt/lists /var/cache/apt

    #RUN apt-get update && apt-get install -y \
    #&& apt-get clean && rm -rf /var/lib/apt/lists /var/cache/apt \

    RUN apk add --no-cache \
        curl \
        nano \
        less \
        bash \
        git \
        sox \
        ffmpeg \
        jpegoptim \
        # test dependenceies - but unpicking/moving them is too hard
        tesseract-ocr \
        jpeg-dev \
        zlib-dev \
        # `Arial` font is needed - maybe this can be changed to `sans-serif`?
        msttcorefonts-installer \
        fontconfig \
    # build font ms-fonts
    && update-ms-fonts && fc-cache -f
    && pip3 install --no-cache-dir --upgrade \
        pip \
        setuptools \
    && true

    # --------------------------------------------------------------------------

    VOLUME /logs
    VOLUME /media/source
    VOLUME /media/meta
    VOLUME /media/processed
    VOLUME /data

    WORKDIR /processmedia2


FROM base as python_dependencies
    COPY requirements.txt ./
    RUN pip3 install --no-cache-dir -r requirements.txt

FROM python_dependencies as python_dependencies_test

    # hack for install pillow - https://genji-games.medium.com/dockerizing-an-app-that-uses-pillow-is-not-a-good-intro-to-docker-a026aa67ce1c
    RUN apk add --no-cache --virtual .build-deps \
        build-base \
        linux-headers \
    && pip install Pillow \
    && apk del .build-deps \
    && true

    COPY ./requirements.test.txt ./
    RUN pip install --no-cache-dir -r requirements.test.txt


FROM python_dependencies as code
    COPY ./processmedia_libs ./processmedia_libs
    COPY \
        *.py \
        config.docker.json \
        logging.json.dist \
        processmedia2.sh \
        config.json.dist \
    ./

FROM code as test
    COPY --from=python_dependencies_test ${PATH_SITE_PACKAGES} ${PATH_SITE_PACKAGES}
    COPY --from=python_dependencies_test /usr/local/bin/pytest /usr/local/bin/pytest
    COPY ./tests ./tests
    COPY ./pytest.ini ./
    RUN pytest -x

# ------------------------------------------------------------------------------

FROM code as production
  CMD ./processmedia2.sh
  # It is possible that encoding could really take more than 30 mins
  HEALTHCHECK --interval=1m --timeout=3s CMD touch -d"-30min" /tmp/marker && [ /processmedia2/data/.heartbeat -nt /tmp/marker ]



#RUN mkdir -p /media/source /media/meta /media/processed && chmod -R 777 /media/

#COPY --from=krallin/ubuntu-tini /usr/local/bin/tini /usr/local/bin/tini
#ENTRYPOINT ["/usr/local/bin/tini", "--", "/processmedia2/docker-compose.yml.processmedia2.sh"]
#https://github.com/docker-library/mysql/issues/47#issuecomment-140339288
#CMD /processmedia2/processmedia2.sh

# docker build -t processmedia2:latest --file .\processmedia2.base.dockerfile .
# docker run -it --rm -v ../:/processmedia2:ro -v /var/run/docker.sock:/var/run/docker.sock docker.io processmedia2:latest
  # Windows -v //var/run/docker.sock:/var/run/docker.sock
