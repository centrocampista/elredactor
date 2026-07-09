from contextlib import asynccontextmanager

from sqlalchemy import text
from .session import AsyncSessionLocal


async def check_db_connection() -> bool:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@asynccontextmanager
async def db_lifespan():
    if not await check_db_connection():
        raise RuntimeError("Cannot connect to database.")
    yield
