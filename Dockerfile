# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

# 1. Install uv for build-time dependency syncing
RUN pip install --no-cache-dir uv

# 2. Copy dependency manifests and install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 3. Install fastapi-cli for running the application
RUN pip install --no-cache-dir fastapi-cli

# 4. Copy application code
COPY . .

# 5. Expose service port
EXPOSE 8000

# 6. Run FastAPI with CLI
CMD ["fastapi", "run"]
