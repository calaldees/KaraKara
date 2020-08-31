FROM python:3-slim as dependencies

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

    # Python dependencies
    COPY requirements.txt ./
    RUN pip3 install --no-cache-dir -r requirements.txt

    # Static web dependencies
    ENV PATH_WRITE==${WORKDIR}/data
    ENV PATH_EXTERNAL=${PATH_WRITE}/externals/static
    RUN mkdir -p ${PATH_EXTERNAL}/images ${PATH_EXTERNAL}/js ${PATH_EXTERNAL}/css ${PATH_EXTERNAL}/fonts

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




FROM dependencies as production
    COPY . /app
    EXPOSE 6543
    VOLUME /logs
    HEALTHCHECK --interval=1m --timeout=3s CMD curl --fail http://127.0.0.1:6543/ || exit 1
    CMD pserve ?/production.ini







#RUN make install
#CMD make run_production


FROM base as test
RUN make test



