FROM node:11-alpine
EXPOSE 8080

# this takes ages, so do it in advance
COPY package.json package-lock.json /app/
WORKDIR /app
RUN npm install

COPY . /app
RUN npm run build
CMD npm run serve
