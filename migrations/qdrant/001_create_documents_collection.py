from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams


async def upgrade(client: AsyncQdrantClient) -> None:
    await client.create_collection(
        collection_name="documents",
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )


async def downgrade(client: AsyncQdrantClient) -> None:
    await client.delete_collection("documents")
