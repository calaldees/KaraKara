FROM node:13 AS build
RUN apt-get update && apt-get install -y util-linux git && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY package.json package-lock.json /app/
WORKDIR /app
RUN npm install

# Build app
COPY . /app
RUN npm run build

# Copy built app to minimal-httpd container
FROM alpine:3.7
EXPOSE 80
VOLUME /logs
HEALTHCHECK --interval=1m --timeout=3s CMD wget -q http://127.0.0.1/ -O /dev/null
RUN apk add --no-cache thttpd
COPY --from=build /app/dist /www
CMD thttpd -D -l /logs/player2.log -d /www
