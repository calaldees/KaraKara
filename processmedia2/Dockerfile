ARG PYTHON_IMAGE_VERSION=3.10
FROM python:${PYTHON_IMAGE_VERSION}-alpine as base
    ARG PYTHON_IMAGE_VERSION
    ENV PATH_SITE_PACKAGES=/usr/local/lib/python${PYTHON_IMAGE_VERSION}/site-packages/

    # System Dependencies ------------------------------------------------------

    # ffmpeg (staticly compiled) with libsvtav1 + h265 support
    COPY --from=mwader/static-ffmpeg /ffmpeg /usr/local/bin/
    COPY --from=mwader/static-ffmpeg /ffprobe /usr/local/bin/
    RUN ffmpeg --help

    RUN apk add --no-cache \
        curl \
        nano \
        less \
        bash \
        git \
        imagemagick \
        # test dependenceies - but unpicking/moving them is too hard
        jpeg-dev \
        zlib-dev \
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

    # hack for install pillow
    # https://genji-games.medium.com/dockerizing-an-app-that-uses-pillow-is-not-a-good-intro-to-docker-a026aa67ce1c
    #RUN apk add --no-cache --virtual .build-deps \
    #    build-base \
    #    linux-headers \
    #&& pip install Pillow \
    #&& apk del .build-deps \
    #&& true

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
  # It is possible that encoding could really take more than 120 mins?
  HEALTHCHECK --interval=1m --timeout=3s CMD touch -d"-120min" /tmp/marker && [ /data/.heartbeat -nt /tmp/marker ]
