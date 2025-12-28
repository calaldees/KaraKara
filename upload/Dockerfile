FROM python:3.14-alpine AS base
WORKDIR /app
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    pip install --no-cache-dir --group dev .
COPY . /app

FROM node:24 AS build-frontend
COPY package.json package-lock.json rsbuild.config.ts tsconfig.json /app/
WORKDIR /app
RUN npm install
COPY frontend /app/frontend
RUN ./node_modules/.bin/rsbuild build --base /upload

FROM base AS test
RUN pytest
RUN mypy .

FROM base AS production
EXPOSE 8000
VOLUME /uploads
COPY --from=build-frontend /app/dist /app/dist/
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000"]
