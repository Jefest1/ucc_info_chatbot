# syntax=docker/dockerfile:1
FROM python:3.11

# Install build dependencies and tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    clang \
    gcc \
    g++ \
    libc-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Download the latest installer
ADD https://astral.sh/uv/0.4.20/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.cargo/bin/:$PATH"
ENV PATH="/app/.venv/bin:$PATH"

# Set workdir
WORKDIR /app

# Add dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code - to get the proper directory structure
COPY . .

# Debug - check file structure
RUN echo "==== DEBUG: Project file structure ====" && \
    ls -la && \
    echo "==== DEBUG: app directory ====" && \
    ls -la app/ && \
    echo "==== DEBUG: Finding main.py ====" && \
    find / -name "main.py" 2>/dev/null | grep -v "__pycache__"

# Expose service port
EXPOSE 8000

# Run application using uvicorn 
# The -m flag ensures Python uses the module system for imports
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]