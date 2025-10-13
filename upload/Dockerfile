FROM python:3.13-alpine AS base

WORKDIR /app

COPY pyproject.toml /app
RUN pip install --no-cache-dir .

COPY . /app
RUN mkdir -p /uploads

EXPOSE 8000
CMD ["uvicorn", "upload:app", "--host", "0.0.0.0", "--port", "8000"]
