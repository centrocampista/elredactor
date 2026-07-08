
from qdrant_client import AsyncQdrantClient
from ..config import settings

def _make_client(api_key: str) -> AsyncQdrantClient:
      return AsyncQdrantClient(
          host=settings.qdrant_service_host,
          port=int(settings.qdrant_service_http_port),
          grpc_port=int(settings.qdrant_service_grpc_port),
          prefer_grpc=settings.qdrant_service_prefer_grpc,
          https=not settings.is_dev,
          api_key=api_key,
      )


qdrant_reader = _make_client(settings.qdrant_service_read_only_api_key)
qdrant_writer = _make_client(settings.qdrant_service_api_key)
