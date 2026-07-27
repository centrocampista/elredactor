# El Redactor

[![CI](https://github.com/centrocampista/elredactor/actions/workflows/ci.yml/badge.svg)](https://github.com/centrocampista/elredactor/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Ruff](https://img.shields.io/badge/lint-ruff-261230.svg)](https://github.com/astral-sh/ruff)

Document ingestion and retrieval service built with FastAPI. The REST API handles authentication,
uploads and document metadata, then hands the work over to a LangGraph agent service via HTTP.
LangGraph owns the data layer — it indexes content into a Qdrant vector store and reads and writes
Postgres — which keeps parsing, embedding and retrieval out of the request path.

> **Status: work in progress.** Upload, users and API-credential auth work end to end.
> The API → LangGraph handoff, indexing and retrieval are not wired up yet — see [Roadmap](#roadmap).

---

## Table of contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech stack](#tech-stack)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [API](#api)
- [Make commands](#make-commands)
- [Testing](#testing)
- [CI/CD](#cicd)
- [Project layout](#project-layout)
- [Roadmap](#roadmap)

---

## Features

- **Document upload** — PDF, DOCX, TXT and Markdown, max 50 MB, MIME-type validated
- **Metadata in PostgreSQL** — async SQLAlchemy 2.0 + Alembic migrations, per-document status
  lifecycle (`pending` → `processing` → `done` / `failed`)
- **API key authentication** — `X-Api-Key` / `X-Api-Secret` credential pairs issued per user
- **Agent service** — LangGraph runs standalone on port `2024` and owns the data layer
  (Qdrant vector store + Postgres); it reads uploaded files from the shared `content` volume
  and chunks them. Model access via OpenRouter, optional LangSmith tracing
- **Path-based file handoff** — the API and the agent service share `./content`, so uploads are
  passed by reference; the HTTP boundary between them carries only ids and questions
- **Full container workflow** — dev / prod Compose overlays, Dev Container, Nginx reverse proxy
- **Test pyramid** — unit / integration / e2e, plus nightly mutation testing

## Architecture

```
                     ┌──────────────────┐
  client ──▶ nginx ──▶    elredactor    │  FastAPI  :8000
                     │     REST API     │
                     └───┬──────────┬───┘
                         │          │  HTTP  (upload, ask)
                         │          ▼
                         │    ┌──────────────┐
                         │    │  langgraph   │  agents  :2024
                         │    └──┬────────┬──┘
                         │       │        │
                         ▼       ▼        ▼
                    ┌──────────────┐  ┌─────────────┐
                    │ postgres_red │  │    qdrant   │
                    │    :5432     │  │ :6333/6334  │
                    └──────────────┘  └─────────────┘

              ┌────────────────────────────────────────┐
              │  shared volume:  ./content → /content  │
              └────────────────────────────────────────┘
                 written by the API · read by langgraph
```

**Request flow.** A client uploads a document to the API. The API authenticates the credential
pair, validates the file, writes it to the shared `content` volume and records the metadata row,
then calls LangGraph over HTTP with the document id — the file itself never travels over the wire
a second time. LangGraph reads it straight off the shared volume, extracts and chunks the text,
embeds the chunks, writes the vectors to Qdrant and updates the document status in Postgres.
A query endpoint (`ask`) follows the same call shape: the API forwards the question, LangGraph
retrieves from Qdrant and answers.

Both services talk to each other over plain HTTP inside the Compose network
(`LANGGRAPH_URL`, default `http://langgraph:2024`), and both mount `./content` at `/content`,
so file handoff is a path reference rather than a payload.

**Layering inside `app/`:** `api` (routing and HTTP concerns) → `crud` (persistence) →
`models` (ORM), with `schemas` for request/response contracts and `domain` for
framework-independent dataclasses passed between layers.

## Tech stack

| Area | Choice |
| --- | --- |
| Runtime | Python 3.12, FastAPI, Uvicorn |
| Database | PostgreSQL 16, SQLAlchemy 2.0 (async, `asyncpg`), Alembic |
| Vector store | Qdrant 1.13 |
| LLM / agents | LangChain, LangGraph, OpenRouter, LangSmith (optional) |
| Parsing | PyMuPDF, docx2txt |
| Packaging | `uv` |
| Quality | ruff, mypy, pytest, pytest-asyncio, Playwright, mutmut |
| Infra | Docker Compose, Nginx, GitHub Actions |

## Quick start

**Prerequisites:** Docker and Docker Compose, `make`.

```bash
git clone https://github.com/centrocampista/elredactor.git
cd elredactor

cp .env-example .env      # then fill in the blanks — see Configuration
make dev                  # build and start with logs (use `make dev-d` for detached)
make migrate              # apply database migrations
```

| Service | URL |
| --- | --- |
| API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |
| LangGraph | http://localhost:2024 |
| Qdrant dashboard | http://localhost:6333/dashboard |
| pgAdmin | http://localhost:5050 |

The dev container mounts the source tree, so `--reload` picks up local edits. A debugpy port
(`5678`) is exposed for attaching a debugger, and `.devcontainer/` is ready for VS Code
Dev Containers.

For production: `make prod` (uses `docker-compose.prod.yml`, builds the `prod` image target
without dev dependencies, and disables `/docs`, `/redoc` and `/openapi.json`).

## Configuration

All settings are read from `.env` via `pydantic-settings` (`app/config.py`).

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `POSTGRES_USER` | yes | — | Database user |
| `POSTGRES_PASSWORD` | yes | — | Database password |
| `POSTGRES_DB` | yes | — | Database name |
| `POSTGRES_HOST` | no | `postgres_red` | Hostname inside the Compose network |
| `POSTGRES_PORT` | no | `5432` | Port published on the host |
| `ENVIRONMENT` | no | `production` | `development` / `staging` / `production` |
| `DEBUG` | no | `false` | FastAPI debug mode |
| `QDRANT_SERVICE_API_KEY` | yes | — | Qdrant read/write key |
| `QDRANT_SERVICE_READ_ONLY_API_KEY` | yes | — | Qdrant read-only key |
| `QDRANT_SERVICE_HTTP_PORT` | yes | `6333` | Qdrant REST port |
| `QDRANT_SERVICE_GRPC_PORT` | yes | `6334` | Qdrant gRPC port |
| `LANGGRAPH_URL` | no | `http://langgraph:2024` | Where the API reaches the agent service |
| `OPENROUTER_API_KEY` | for agents | — | OpenRouter key |
| `OPENROUTER_MODEL` | no | `anthropic/claude-haiku-4.5` | Chat model |
| `OPENROUTER_EMBEDDING_MODEL` | no | `openai/text-embedding-3-small` | Embedding model |
| `LANGSMITH_TRACING` | no | `false` | Enable LangSmith tracing |
| `LANGSMITH_API_KEY` | no | — | Required when tracing is on |
| `PGADMIN_EMAIL` / `PGADMIN_PASSWORD` | dev only | — | pgAdmin login |

`ENVIRONMENT=production` hides the OpenAPI docs endpoints and trims the health response.

## API

Base path: `/v1`. Interactive docs at `/docs` outside production.

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/health` | — | Liveness probe |
| `POST` | `/v1/users` | — | Create a user |
| `PATCH` | `/v1/users` | API key | Update a user |
| `POST` | `/v1/api-creds` | — | Issue an API key/secret pair for an existing user |
| `POST` | `/v1/documents/upload` | API key | Upload a document (`multipart/form-data`) |
| `POST` | `/v1/ask` | API key | *(planned)* Ask a question over the indexed corpus |

Authenticated requests send both credential headers:

```bash
curl -X POST http://localhost:8000/v1/documents/upload \
  -H "X-Api-Key: $API_KEY" \
  -H "X-Api-Secret: $API_SECRET" \
  -F "file=@contract.pdf"
```

```json
{
  "id": "6f1a...",
  "filename": "contract.pdf",
  "extension": ".pdf",
  "doc_status": "pending"
}
```

**Error responses:** `401` invalid credentials · `409` email already exists ·
`413` file over 50 MB · `415` unsupported MIME type · `422` missing filename.

## Make commands

`make` with no arguments prints the full list.

| Command | Description |
| --- | --- |
| `make dev` / `make dev-d` | Start the dev stack, attached / detached |
| `make down` | Stop the stack |
| `make logs` / `make logs-db` | Tail app / database logs |
| `make shell` / `make db-shell` | Shell in the app container / `psql` |
| `make test` | Run the whole suite |
| `make test-unit` / `test-integration` / `test-e2e` | Run one layer |
| `make test-cov` | Coverage report (HTML) |
| `make lint` / `make lint-fix` / `make format` | ruff |
| `make migrate` / `migrate-down` | Alembic upgrade head / downgrade one |
| `make migrate-new name="add table"` | Autogenerate a migration |
| `make migrate-history` | Migration history |
| `make prod` / `prod-down` / `prod-logs` | Production stack |
| `make ps` / `build` / `rebuild` / `prune` | Docker housekeeping |

## Testing

Tests are split by the external dependencies they need, and marked accordingly
(`unit`, `integration`, `e2e`):

| Layer | Needs | Location |
| --- | --- | --- |
| Unit | nothing | `tests/unit/` |
| Integration | PostgreSQL + Qdrant | `tests/integration/` |
| E2E | full stack + Playwright | `tests/e2e/` |

```bash
make test-unit
make test-cov     # htmlcov/index.html
```

Mutation testing runs nightly with `mutmut` (`app/` as source, e2e excluded); it can be run
locally with `uv run mutmut run` followed by `uv run mutmut results`.

## CI/CD

`ci.yml` runs on every push and on PRs to `main`:

1. **Lint & format** — `ruff check` and `ruff format --check`
2. **Type check** — `mypy app/` with the Pydantic plugin
3. **Unit tests**
4. **Integration tests** — against PostgreSQL and Qdrant service containers, migrations applied first
5. **Docker build** — production image target

Two automation jobs sit on top:

- **Report CI failure** — opens a GitHub issue tagged with a per-branch label when the pipeline
  fails, and comments on the existing issue instead of creating duplicates. Issues are
  auto-closed on merge by `close-issue.yml`.
- **Create PR → main** — opens a pull request from a feature branch if one doesn't exist yet.

`nightly.yml` runs mutation tests on a schedule.

## Project layout

```
app/
├── api/v1/routers/   # HTTP endpoints, dependencies, constants
├── agents/           # LangGraph graphs, nodes, prompts, tools, state
├── crud/             # database operations
├── db/               # engine, session, base, lifespan, mixins
├── domain/           # framework-independent dataclasses
├── models/           # SQLAlchemy ORM models
├── schemas/          # Pydantic request/response models
├── vector_db/        # Qdrant client and lifespan
├── config.py         # settings
└── main.py           # app factory and router registration
migrations/           # Alembic
nginx/conf.d/         # HTTP and HTTPS reverse proxy configs
tests/                # unit / integration / e2e
```

## Roadmap

- [x] User accounts and API-credential auth
- [x] Document upload with validation and metadata persistence
- [x] CI pipeline with automated failure tracking
- [ ] Mount `./content` into the `langgraph` service as well
- [ ] API → LangGraph HTTP client, called from the upload endpoint
- [ ] Ingestion graph: read from `/content`, extract text (PyMuPDF, docx2txt), chunk, embed, index into Qdrant
- [ ] Document status transitions (`processing` → `done` / `failed`) written back from LangGraph
- [ ] Retrieval graph and the `ask` endpoint
- [ ] OIDC login flow with a mock provider for CI

## License

Not yet specified.