FROM debian:8.2

RUN apt-add-repository ppa:nginx/development
RUN apt-get update && apt-get install -yq \
        curl \
        nginx \
        postgresql \
        python-virtualenv \
        python3-setuptools \
        python3-dev \
    && apt-get clean
#RUN update-rc.d -f nginx disable

RUN	sudo -u postgres psql -c "create user karakara with password 'karakara';" || true
RUN sudo -u postgres psql -c "create database karakara with owner karakara encoding 'utf8' TEMPLATE=template0 LC_CTYPE='en_US.UTF-8' LC_COLLATE='en_US.UTF-8';" || true

