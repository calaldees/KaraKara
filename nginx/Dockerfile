FROM nginx:alpine
EXPOSE 80
VOLUME /logs
VOLUME /media/processed
HEALTHCHECK --interval=1m --timeout=3s CMD wget -q http://127.0.0.1/files/ -O /dev/null

COPY nginx.conf /etc/nginx/nginx.conf
COPY www /app/www
