# syntax=docker/dockerfile:1
FROM python:3.11

# Install build dependencies and tools
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download the latest installer
ADD https://astral.sh/uv/0.5.26/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
# ENV PATH="/root/.cargo/bin/:$PATH"
# ENV PATH="/app/.venv/bin:$PATH"
ENV PATH="/root/.local/bin/:$PATH"

# Set workdir
WORKDIR /app

# Add dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application code - to get the proper directory structure
COPY ./app .

# Expose service port
EXPOSE 8000


# Run using uv and uvicorn
# CMD [ "uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]
CMD [ "uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" ]
# CMD ["sleep", "infinity"]
