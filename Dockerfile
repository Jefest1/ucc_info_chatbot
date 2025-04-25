# syntax=docker/dockerfile:1
#### Builder Stage ####
FROM python:3.12-slim-bookworm AS builder

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /bin/uv

ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1
WORKDIR /app

# Cache installs: copy both lockfile and project file
COPY uv.lock pyproject.toml ./

# Install dependencies (no project install yet)
RUN --mount=type=cache,target=/root/.cache/uv \
    /bin/uv sync --frozen --no-install-project --no-dev

# Copy source then install project itself
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    /bin/uv sync --frozen --no-dev

#### Runtime Stage ####
FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app
COPY --from=builder /app /app
EXPOSE 8000

CMD ["uv", "run", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
