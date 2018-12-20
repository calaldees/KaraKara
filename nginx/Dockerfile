FROM nginx:mainline-alpine
EXPOSE 80
VOLUME /media/processed

COPY . /app
RUN cp /app/nginx.conf /etc/nginx/nginx.conf
CMD nginx -g 'daemon off;'
