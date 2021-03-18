FROM ubuntu:latest AS auth-http

ENV MOSQUITTO_VERSION=1.6.14
# ENV MOSQUITTO_VERSION=2.0.4

RUN apt-get update && apt-get install -y --no-install-recommends \
    libc-ares-dev git libmysqlclient-dev libssl-dev uuid-dev build-essential wget ca-certificates \
    curl libcurl4-openssl-dev libc-ares2 libcurl4 libwebsockets-dev

RUN cd /tmp \
    && wget http://mosquitto.org/files/source/mosquitto-$MOSQUITTO_VERSION.tar.gz -O mosquitto.tar.gz \
    && mkdir mosquitto-src && tar xfz mosquitto.tar.gz --strip-components=1 -C mosquitto-src \
    && cd mosquitto-src \
    && make WITH_SRV=yes WITH_MEMORY_TRACKING=no WITH_WEBSOCKETS=yes \
    && make install && ldconfig

COPY auth-http.c /tmp
# gcc -I<path to mosquitto_plugin.h> -fPIC -shared plugin.c -o plugin.so
RUN gcc -fPIC -shared /tmp/auth-http.c -o /usr/local/lib/auth-http.so

FROM eclipse-mosquitto:1.6
EXPOSE 1883
EXPOSE 9001
COPY --from=auth-http /usr/local/lib/auth-http.so /usr/local/lib/auth-http.so
COPY mosquitto.conf /mosquitto/config/
