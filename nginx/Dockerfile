FROM nginx:mainline-alpine
COPY . /app
CMD /bin/sh -c "DOLLAR='$$' envsubst < /app/nginx.conf > /etc/nginx/nginx.conf && nginx -g 'daemon off;'"
