FROM python:3.13-alpine AS base

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir .
RUN mkdir -p /uploads

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
