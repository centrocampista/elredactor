# === base ===
FROM python:3.13-slim AS base

WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./

# === dev ===
FROM base AS dev

# installs prod + dev (pytest, debugpy, ruff, playwright)
RUN uv sync --frozen

# installs playwright
RUN uv run playwright install --with-deps chromium

COPY . .

# === prod ===
FROM base AS prod

RUN uv sync --frozen --no-dev
COPY . .