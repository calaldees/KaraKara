FROM node:18 AS build
RUN apt-get update && apt-get install -y util-linux git && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY package.json package-lock.json /app/
WORKDIR /app
RUN npm install

# Build app
COPY . /app
RUN npm run test
RUN npm run build

# Copy built app to minimal-httpd container
FROM alpine:3.7
EXPOSE 80
HEALTHCHECK --interval=1m --timeout=3s CMD wget -q http://127.0.0.1/ -O /dev/null
RUN apk add --no-cache thttpd
COPY --from=build /app/dist /www
RUN mkdir /www/errors && cd /www/errors && ln -s ../index.html 404.html
CMD thttpd -D -d /www
