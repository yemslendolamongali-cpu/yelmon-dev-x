# Stage 1: Build frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --prefer-offline --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements-cloud.txt .
RUN pip install --no-cache-dir -r requirements-cloud.txt

COPY backend/ backend/
COPY assets/ assets/
RUN mkdir -p logs data

COPY --from=frontend-build /app/frontend/build/ frontend/build/

ENV YELMON_HOST=0.0.0.0
ENV YELMON_PORT=10000
ENV PYTHONUNBUFFERED=1

EXPOSE 10000

CMD gunicorn --worker-class eventlet --workers 1 --bind 0.0.0.0:${PORT:-10000} backend.app:app
