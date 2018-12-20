FROM nginx:mainline-alpine
EXPOSE 80
VOLUME /media/processed
HEALTHCHECK --interval=1m --timeout=3s CMD curl --fail http://127.0.0.1/files/ || exit 1

RUN apk --no-cache add curl

COPY . /app
RUN cp /app/nginx.conf /etc/nginx/nginx.conf
CMD nginx -g 'daemon off;'
