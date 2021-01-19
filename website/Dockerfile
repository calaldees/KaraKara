FROM python:3-slim as base

    # System dependencies
    RUN apt-get update && apt-get install -y \
        git \
        curl \
        nano \
        less \
        make \
    && pip install --no-cache-dir --upgrade \
        pip \
        setuptools \
    && true

    ENV WORKDIR=/app
    WORKDIR ${WORKDIR}

    ENV PATH_WRITE=/appdata
    RUN mkdir -p ${PATH_WRITE}

    ENV PATH_LOCALE=${PATH_WRITE}/locale

FROM base as python_dependencies
    COPY requirements.txt ./
    RUN pip3 install --no-cache-dir -r requirements.txt
FROM python_dependencies as python_dependencies_test
    COPY ./requirements.test.txt ./
    RUN pip install --no-cache-dir -r requirements.test.txt

# -- Static web dependencies

FROM base as static

    ENV PATH_EXTERNAL=${PATH_WRITE}/externals/static
    RUN mkdir -p \
      ${PATH_EXTERNAL}/images \
      ${PATH_EXTERNAL}/js \
      ${PATH_EXTERNAL}/css \
      ${PATH_EXTERNAL}/fonts

    ENV VERSION_JQUERY=2.1.4
        RUN \
            curl "http://code.jquery.com/jquery-${VERSION_JQUERY}.min.js" -o "${PATH_EXTERNAL}/jquery.min.js" &&\
            curl "http://code.jquery.com/jquery-${VERSION_JQUERY}.min.map" -o "${PATH_EXTERNAL}/jquery-${VERSION_JQUERY}.min.map"
    ENV VERSION_JQUERY_COOKIE=1.4.0
        RUN \
            curl "http://raw.github.com/carhartl/jquery-cookie/v${VERSION_JQUERY_COOKIE}/jquery.cookie.js" -o "${PATH_EXTERNAL}/jquery.cookie.js"
    ENV VERSION_JQUERY_SORTABLE=master
        RUN \
            curl "https://raw.github.com/farhadi/html5sortable/${VERSION_JQUERY_SORTABLE}/jquery.sortable.js" -o "${PATH_EXTERNAL}/jquery.sortable.js"
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
            BOOTSTRAP_URL="http://raw.github.com/twbs/bootstrap/v${VERSION_BOOTSTRAP}/dist/" &&\
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

# --- locale
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


# --- config
#FROM base as config
FROM python_dependencies_test as xxx
    ENV PATH_CONFIG=${PATH_WRITE}/config
    ENV INI_DEV=${PATH_CONFIG}/development.ini
    COPY ./config/development.ini.dist ${INI_DEV}
    COPY ./config/search_config.json.dist ${PATH_CONFIG}/search_config.json

# --- test
#FROM python_dependencies_test as test
    COPY ./config/test.inidiff.dist ${PATH_CONFIG}/test.inidiff
    RUN python -m calaldees.apps.make_ini \
        ${INI_DEV} \
        ${PATH_CONFIG}/test.inidiff \
        ${PATH_CONFIG}/test.ini
    COPY ./karakara ./karakara
    COPY ./tests ./tests
    COPY ./setup.py ./
    COPY --from=locale ${PATH_LOCALE} ${PATH_LOCALE}
    RUN pip install -e .
    RUN pytest --ini_file=${PATH_CONFIG}/test.ini -x



FROM python_dependencies as production
    #COPY . /app
    COPY ./config/production.inidiff ${PATH_CONFIG}/
    RUN python -m calaldees.apps.make_ini \
        ${INI_DEV} \
        ${PATH_CONFIG)/production.inidiff \
        ${PATH_CONFIG}/production.ini
    EXPOSE 6543
    VOLUME /logs
    HEALTHCHECK --interval=1m --timeout=3s CMD curl --fail http://127.0.0.1:6543/ || exit 1
    CMD pserve ${PATH_CONFIG}/production.ini

#RUN make install
#CMD make run_production





