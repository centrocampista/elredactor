from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any

from fastapi import FastAPI

from app.api.v1.routers import documents
from app.db.lifespan import db_lifespan
from app.vector_db.lifespan import qdrant_lifespan
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(db_lifespan())
        await stack.enter_async_context(qdrant_lifespan())
        yield


app = FastAPI(
    title="El Redactor",
    version="0.1.0",
    docs_url="/docs" if not settings.is_prod else None,
    redoc_url="/redoc" if not settings.is_prod else None,
    openapi_url="/openapi.json" if not settings.is_prod else None,
    debug=settings.debug,
)

app.include_router(documents.router, prefix="/v1/documents")


@app.get("/health")
async def health() -> dict:
    response: dict[str, Any] = {"status": "ok"}
    if settings.is_dev:
        response["environment"] = settings.environment
        response["debug"] = settings.debug
    return response
