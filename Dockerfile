# syntax=docker/dockerfile:1

#### Builder Stage ####
FROM python:3.12-slim-bookworm AS builder

# 1. Copy uv binary from Astral’s distroless image
COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /bin/uv

# 2. uv environment
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

# 3. Cache installs: copy both lockfile and pyproject
COPY uv.lock pyproject.toml ./

# 4. Install all dependencies (no project yet)
RUN --mount=type=cache,target=/root/.cache/uv \
    /bin/uv sync --frozen --no-install-project --no-dev

# 5. Copy source and install your project
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    /bin/uv sync --frozen --no-dev

#### Runtime Stage ####
FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

# 6. Copy installed Python packages and uv binary from builder
COPY --from=builder /usr/local /usr/local
COPY --from=builder /bin/uv /bin/uv

# 7. Copy only your application code
COPY . .

# 8. Expose FastAPI port
EXPOSE 8000

# 9. Start via uvicorn
WORKDIR /app
CMD ["/usr/local/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
