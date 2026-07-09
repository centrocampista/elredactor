from contextlib import asynccontextmanager
from .session import qdrant_reader, qdrant_writer


@asynccontextmanager
async def qdrant_lifespan():
    if not await check_qdrant():
        raise RuntimeError("Couldn't connect to Qdrant vector database")
    yield
    await qdrant_reader.close()
    await qdrant_writer.close()


async def check_qdrant() -> bool:
    try:
        await qdrant_reader.get_collections()
        return True
    except Exception:
        return False
