FROM python:3.13-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml for dependencies
COPY pyproject.toml /app/pyproject.toml

# Install Python dependencies
RUN pip install --no-cache-dir -e ".[server]"

# Development stage
FROM base as development
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "server.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

# Production API stage
FROM base as api
COPY . /app
CMD ["uvicorn", "server.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# Production worker stage
FROM base as worker
COPY . /app
CMD ["celery", "-A", "workers.celery_app", "worker", "--loglevel=info", "--concurrency=2"]
