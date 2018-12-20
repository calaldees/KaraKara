FROM node:11
EXPOSE 8080
RUN npm install http-server -g

# this takes ages, so do it in advance
COPY package.json package-lock.json /app/
WORKDIR /app
RUN npm install

COPY . /app
RUN npm run build
CMD http-server ./dist/
