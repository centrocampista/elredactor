# === base ===
FROM python:3.13-slim AS base

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN pip install uv
COPY pyproject.toml .

# === dev ===
FROM base AS dev

# installs prod + dev (pytest, debugpy, ruff, playwright)
RUN uv sync

# dependencies for playwright
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# installs playwright
RUN uv run playwright install chromium

COPY . .

# === prod ===
FROM base AS prod

RUN uv sync --no-dev
COPY . .