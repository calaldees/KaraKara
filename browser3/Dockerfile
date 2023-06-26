FROM node:18 AS build
RUN apt-get update && apt-get install -y util-linux git && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY package.json package-lock.json /app/
WORKDIR /app
RUN npm install

# Build app
COPY . /app
RUN npm run test-once
RUN npm run build

# Copy built app to httpd container
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
