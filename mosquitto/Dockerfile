FROM ubuntu:latest AS auth-karakara

ENV MOSQUITTO_VERSION=1.6.14

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential wget libwebsockets-dev libc-ares-dev libcurl4-openssl-dev

RUN cd /tmp \
    && wget http://mosquitto.org/files/source/mosquitto-$MOSQUITTO_VERSION.tar.gz -O mosquitto.tar.gz \
    && mkdir mosquitto-src && tar xfz mosquitto.tar.gz --strip-components=1 -C mosquitto-src \
    && cd mosquitto-src \
    && make WITH_SRV=yes WITH_MEMORY_TRACKING=no WITH_WEBSOCKETS=yes \
    && make install && ldconfig

COPY auth-karakara.c /tmp
# gcc -I<path to mosquitto_plugin.h> -fPIC -shared plugin.c -o plugin.so
RUN gcc -fPIC -shared /tmp/auth-karakara.c -lcurl -o /usr/local/lib/auth-karakara.so

FROM eclipse-mosquitto:1.6
EXPOSE 1883
EXPOSE 9001
RUN apk add --no-cache libcurl
COPY --from=auth-karakara /usr/local/lib/auth-karakara.so /usr/local/lib/auth-karakara.so
COPY mosquitto.conf /mosquitto/config/
