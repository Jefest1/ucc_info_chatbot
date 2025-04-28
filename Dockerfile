# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

# 1. Copy the uv binary
COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /bin/uv

# 2. Set workdir and bring in your entire source
WORKDIR /app
COPY . .

# 3. Install all dependencies in one step
RUN uv sync --frozen --no-dev

# 4. Expose and run
EXPOSE 8000
CMD ["uv", "run", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
