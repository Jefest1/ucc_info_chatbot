# syntax=docker/dockerfile:1

FROM python:3.12-slim-bookworm

# Copy uv binary from Astral's distroless image
COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /bin/uv

# Set environment variables
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONPATH=/

# Working directory
WORKDIR /app

# Copy application code
COPY . .

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    /bin/uv sync --frozen --no-dev

# Verify file structure for debugging
RUN find . -type f -name "*.py" | grep -v "__pycache__" | sort

# Expose port
EXPOSE 8000

# Create non-root user
RUN addgroup --system mygroup && \
    adduser --system --ingroup mygroup myuser && \
    chown -R myuser:mygroup /app

USER myuser

# Run application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
