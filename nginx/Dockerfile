FROM nginx:alpine
EXPOSE 80
VOLUME /logs
VOLUME /media/processed
HEALTHCHECK --interval=1m --timeout=3s CMD curl --fail http://127.0.0.1/files/ || exit 1

RUN apk --no-cache add curl

COPY nginx.conf /etc/nginx/nginx.conf
COPY www /app/www
