import asyncio
import importlib
import os

import asyncpg
from qdrant_client import AsyncQdrantClient

from app.config import settings

MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__))
MIGRATIONS_PACKAGE = "migrations.qdrant"


def _pg_url() -> str:
    # asyncpg does not understand the SQLAlchemy scheme prefix (postgresql+asyncpg://)
    return settings.database_url.replace("postgresql+asyncpg://", "postgresql://")


async def get_applied(pg_conn) -> set[str]:
    rows = await pg_conn.fetch("SELECT version FROM qdrant_migrations")
    return {row["version"] for row in rows}


async def mark_applied(pg_conn, version: str) -> None:
    await pg_conn.execute(
        "INSERT INTO qdrant_migrations (version) VALUES ($1)", version
    )


async def upgrade_head() -> None:
    pg_conn = await asyncpg.connect(_pg_url())
    qdrant = AsyncQdrantClient(
        host=settings.qdrant_service_host,
        port=int(settings.qdrant_service_http_port),
        api_key=settings.qdrant_service_api_key,
        https=False,
    )

    try:
        applied = await get_applied(pg_conn)

        files = sorted(
            [
                f[:-3]
                for f in os.listdir(MIGRATIONS_DIR)
                if f.endswith(".py") and not f.startswith("_") and f != "runner.py"
            ]
        )

        for version in files:
            if version in applied:
                print(f"[skip] {version}")
                continue
            module = importlib.import_module(f"{MIGRATIONS_PACKAGE}.{version}")
            await module.upgrade(qdrant)
            await mark_applied(pg_conn, version)
            print(f"[ok]   {version}")

    finally:
        await pg_conn.close()
        await qdrant.close()


if __name__ == "__main__":
    asyncio.run(upgrade_head())
