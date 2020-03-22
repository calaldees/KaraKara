FROM node:11
EXPOSE 80
VOLUME /logs
HEALTHCHECK --interval=1m --timeout=3s CMD curl --fail http://127.0.0.1/ || exit 1

RUN apt-get update && apt-get install -y util-linux curl git && rm -rf /var/lib/apt/lists/*

# this takes ages, so do it in advance
COPY package.json package-lock.json /app/
WORKDIR /app
RUN npm install

COPY . /app
RUN npm run build

# https://github.com/parcel-bundler/parcel/issues/857
#CMD npm run serve
RUN npm install -g http-server
CMD http-server -p 80 dist >>/logs/player2-access.log 2>>/logs/player2-error.log
