# Use the official Python slim base image (small, production-oriented)
FROM python:3.12-slim

# Set the working directory to the container root (project root)
WORKDIR /

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install the 'uv' tool for managing Python dependencies
RUN pip install --no-cache-dir uv

# Copy only dependency files first (leverage Docker cache)
COPY pyproject.toml uv.lock ./

# Install dependencies from the lockfile (exact versions, no dev dependencies)
RUN uv sync --frozen --no-dev

# Copy the entire app code (uses .dockerignore to exclude .git, .venv, etc.)
COPY . .

# Run the FastAPI app with Uvicorn via 'uv run'
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
