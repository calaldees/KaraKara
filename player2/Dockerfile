FROM node:11-alpine
EXPOSE 80

# npm uses lscpu
RUN apk --no-cache add util-linux

# this takes ages, so do it in advance
COPY package.json package-lock.json /app/
WORKDIR /app
RUN npm install

COPY . /app
RUN npm run build

# https://github.com/parcel-bundler/parcel/issues/857
#CMD npm run serve
RUN npm install -g http-server
CMD http-server -p 80 dist
