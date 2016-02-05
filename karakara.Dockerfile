FROM debian:8.3

RUN apt-get update && apt-get install -yq --fix-missing \
        make \
        software-properties-common \
        curl \
        python-virtualenv \
        python3-setuptools \
        python3-dev \
        nginx \
        postgresql \
    && apt-get clean

#RUN apt-add-repository ppa:nginx/development
#RUN update-rc.d -f nginx disable

COPY karakara.Dockerfile.sql /tmp/
RUN	service postgresql start && su postgres -c "psql -f /tmp/karakara.Dockerfile.sql"

ENV PYTHON_ENV /python_env/
ENV MAKE /usr/bin/make --directory /karakara/

RUN ${MAKE}website install
RUN ${MAKE}website test

EXPOSE 6543
EXPOSE 9873

CMD service postgresql start && /usr/bin/make --directory /karakara/website/ run_production