ARG PYTHON_IMAGE_VERSION=3.9
FROM python:${PYTHON_IMAGE_VERSION}-slim as base
    ARG PYTHON_IMAGE_VERSION
    ENV PATH_SITE_PACKAGES=/usr/local/lib/python${PYTHON_IMAGE_VERSION}/site-packages/

    # System dependencies
    RUN apt-get update && apt-get install -y \
        git \
        curl \
        nano \
        less \
    && pip install --no-cache-dir --upgrade \
        pip \
        setuptools \
    && true

# Maybe move these ENV's to after dependencies? - that would mean copying the dependecies folder? humm ...
    ENV WORKDIR=/app
    WORKDIR ${WORKDIR}
    ENV PYTHONPATH=${WORKDIR}

    ENV PATH_WRITE=/appdata
    ENV PATH_LOCALE=${PATH_WRITE}/locale
    ENV PATH_EXTERNAL=${PATH_WRITE}/externals/static

FROM base as python_dependencies
    COPY ./requirements.txt ./
    RUN pip3 install --no-cache-dir -r requirements.txt
FROM python_dependencies as python_dependencies_test
    COPY ./requirements.test.txt ./
    RUN pip install --no-cache-dir -r requirements.test.txt


FROM base as static
    RUN mkdir -p \
      ${PATH_EXTERNAL}/images \
      ${PATH_EXTERNAL}/js \
      ${PATH_EXTERNAL}/css \
      ${PATH_EXTERNAL}/fonts

    ENV URL_GITHUB_RAW="https://raw.githubusercontent.com"

    ENV VERSION_JQUERY=2.1.4
        RUN \
            curl "http://code.jquery.com/jquery-${VERSION_JQUERY}.min.js" -o "${PATH_EXTERNAL}/jquery.min.js" &&\
            curl "http://code.jquery.com/jquery-${VERSION_JQUERY}.min.map" -o "${PATH_EXTERNAL}/jquery-${VERSION_JQUERY}.min.map"
    ENV VERSION_JQUERY_COOKIE=1.4.0
        RUN \
            curl "${URL_GITHUB_RAW}/carhartl/jquery-cookie/v${VERSION_JQUERY_COOKIE}/jquery.cookie.js" -o "${PATH_EXTERNAL}/jquery.cookie.js"
    ENV VERSION_JQUERY_SORTABLE=master
        RUN \
            curl "${URL_GITHUB_RAW}/farhadi/html5sortable/${VERSION_JQUERY_SORTABLE}/jquery.sortable.js" -o "${PATH_EXTERNAL}/jquery.sortable.js"
    ENV VERSION_JQUERY_MOBILE=1.4.5
        RUN \
            curl "http://code.jquery.com/mobile/${VERSION_JQUERY_MOBILE}/jquery.mobile-${VERSION_JQUERY_MOBILE}.min.js" -o "${PATH_EXTERNAL}/jquery.mobile.min.js" &&\
            curl "http://code.jquery.com/mobile/${VERSION_JQUERY_MOBILE}/jquery.mobile-${VERSION_JQUERY_MOBILE}.min.css" -o "${PATH_EXTERNAL}/jquery.mobile.min.css" &&\
            curl "http://code.jquery.com/mobile/${VERSION_JQUERY_MOBILE}/jquery.mobile-${VERSION_JQUERY_MOBILE}.min.map" -o "${PATH_EXTERNAL}/jquery.mobile.min.map" &&\
            curl "http://code.jquery.com/mobile/${VERSION_JQUERY_MOBILE}/images/ajax-loader.gif" -o "${PATH_EXTERNAL}/images/ajax-loader.gif"
    ENV VERSION_YUI_RESET=3.18.1
        RUN \
            curl "http://yui.yahooapis.com/${VERSION_YUI_RESET}/build/cssreset/cssreset-min.css" -o "${PATH_EXTERNAL}/cssreset-min.css"
    ENV VERSION_BOOTSTRAP=3.3.7
        RUN \
            BOOTSTRAP_URL="${URL_GITHUB_RAW}/twbs/bootstrap/v${VERSION_BOOTSTRAP}/dist" &&\
            curl "${BOOTSTRAP_URL}/js/bootstrap.min.js" \
              -o "${PATH_EXTERNAL}/js/bootstrap.min.js" &&\
            curl "${BOOTSTRAP_URL}/css/bootstrap-theme.min.css" \
              -o "${PATH_EXTERNAL}/css/bootstrap-theme.min.css" &&\
            curl "${BOOTSTRAP_URL}/css/bootstrap.min.css" \
              -o "${PATH_EXTERNAL}/css/bootstrap.min.css" &&\
            curl "${BOOTSTRAP_URL}/fonts/glyphicons-halflings-regular.woff" \
              -o "${PATH_EXTERNAL}/fonts/glyphicons-halflings-regular.woff" &&\
            curl "${BOOTSTRAP_URL}/fonts/glyphicons-halflings-regular.woff2" \
              -o "${PATH_EXTERNAL}/fonts/glyphicons-halflings-regular.woff2" &&\
            curl "${BOOTSTRAP_URL}/fonts/glyphicons-halflings-regular.ttf" \
              -o "${PATH_EXTERNAL}/fonts/glyphicons-halflings-regular.ttf" &&\
            curl "${BOOTSTRAP_URL}/fonts/glyphicons-halflings-regular.eot" \
              -o "${PATH_EXTERNAL}/fonts/glyphicons-halflings-regular.eot" &&\
            curl "${BOOTSTRAP_URL}/fonts/glyphicons-halflings-regular.svg" \
              -o "${PATH_EXTERNAL}/fonts/glyphicons-halflings-regular.svg" &&\
            true
    ENV VERSION_MQTT=1.0.1
        RUN \
            curl "https://cdnjs.cloudflare.com/ajax/libs/paho-mqtt/${VERSION_MQTT}/mqttws31.min.js" -o "${PATH_EXTERNAL}/mqttws31.min.js"
    RUN [ `find ${PATH_EXTERNAL} -empty` == ""]



FROM python_dependencies as locale
    RUN mkdir -p ${PATH_LOCALE}

    # extract messages from source files and generate a POT file
    COPY ./karakara ./karakara
    COPY ./locale/babel_message_extractors.ini ${PATH_LOCALE}/
    RUN pybabel extract \
        --mapping=${PATH_LOCALE}/babel_message_extractors.ini \
        --output=${PATH_LOCALE}/karakara.pot \
        karakara

    # update existing message catalogs (po files) from a POT file
    COPY \
        ./locale/en/LC_MESSAGES/karakara.po \
        ${PATH_LOCALE}/en/LC_MESSAGES/karakara.po
    RUN pybabel update \
        --domain=karakara \
        --output-dir=${PATH_LOCALE} \
        --input-file=${PATH_LOCALE}/karakara.pot \
        --locale=en \
        --previous true
    # TODO: expose this to host? `docker cp`?

    # compile message catalogs (po files) to MO files (binary for gettext)
    RUN pybabel compile \
        --domain=karakara \
        --directory=${PATH_LOCALE} \
        --statistics true


FROM python_dependencies as code
    COPY ./karakara ./karakara
    COPY --from=locale ${PATH_LOCALE} ${PATH_LOCALE}
    COPY --from=static ${PATH_EXTERNAL} ${PATH_EXTERNAL}

    ENV PATH_CONFIG=${PATH_WRITE}/config
    COPY ./config/development.ini.dist ${PATH_CONFIG}/development.ini
    COPY ./config/search_config.json.dist ${PATH_CONFIG}/search_config.json

    EXPOSE 6543
    VOLUME /logs

FROM code as development
    CMD pserve ${PATH_CONFIG}/development.ini

FROM code as test
    COPY --from=python_dependencies_test ${PATH_SITE_PACKAGES} ${PATH_SITE_PACKAGES}
    COPY --from=python_dependencies_test /usr/local/bin/pytest /usr/local/bin/pytest
    COPY ./tests ./tests
    COPY ./pytest.ini ./
    COPY ./config/test.inidiff.dist ${PATH_CONFIG}/test.inidiff
    RUN python -m calaldees.apps.make_ini \
        ${PATH_CONFIG}/development.ini \
        ${PATH_CONFIG}/test.inidiff \
        ${PATH_CONFIG}/test.ini
    RUN pytest --ini_file=${PATH_CONFIG}/test.ini -x

FROM code as production
    COPY ./config/production.inidiff.dist ${PATH_CONFIG}/production.inidiff
    RUN python -m calaldees.apps.make_ini \
        ${PATH_CONFIG}/development.ini \
        ${PATH_CONFIG}/production.inidiff \
        ${PATH_CONFIG}/production.ini
    CMD pserve ${PATH_CONFIG}/production.ini
    HEALTHCHECK --interval=1m --timeout=3s CMD curl --fail http://127.0.0.1:6543/ || exit 1
