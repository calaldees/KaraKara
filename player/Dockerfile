FROM node:11-alpine
EXPOSE 80
HEALTHCHECK --interval=1m --timeout=3s CMD curl --fail http://127.0.0.1/ || exit 1

RUN apk --no-cache add util-linux curl

WORKDIR /app
COPY . /app
RUN npm install -g http-server
CMD http-server -p 80 .
