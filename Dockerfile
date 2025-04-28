# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /

# 1. Install uv for build-time dependency syncing
RUN pip install --no-cache-dir uv

# 2. Copy dependency manifests and install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 3. Copy application code
COPY . .

# 4. Expose service port
EXPOSE 8000

# 5. Run Uvicorn directly (no runtime venv creation)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
