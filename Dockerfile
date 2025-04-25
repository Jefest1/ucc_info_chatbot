# syntax=docker/dockerfile:1

#### Builder Stage ####
FROM python:3.12-slim-bookworm AS builder

# Copy uv binary from Astral's distroless image
COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /bin/uv

# Set environment variables
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

# Copy pyproject and lockfile
COPY uv.lock pyproject.toml ./

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    /bin/uv sync --frozen --no-install-project --no-dev

# Copy source code
COPY . .

# Install project
RUN --mount=type=cache,target=/root/.cache/uv \
    /bin/uv sync --frozen --no-dev

#### Runtime Stage ####
FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

# Copy installed packages
COPY --from=builder /usr/local /usr/local

# Copy uv binary
COPY --from=builder /bin/uv /bin/uv

# Copy source code
COPY . .

# Verify file structure for debugging
RUN find /app -type f -name "*.py" | sort

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app

# Create non-root user
RUN addgroup --system mygroup && \
    adduser --system --ingroup mygroup myuser

# Make sure permissions are correctly set
RUN chown -R myuser:mygroup /app

USER myuser

# Health check
HEALTHCHECK --interval=5m --timeout=3s \
  CMD curl -f http://localhost:8000/ || exit 1

# Run application - explicit path
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
