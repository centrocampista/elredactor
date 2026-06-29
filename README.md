# elredactor
Document ingestion and retrieval service built with FastAPI. Indexes and stores documents in both a SQL database and a vector store, enabling structured queries and semantic search over uploaded content.

uv add fastapi uvicorn[standard] sqlalchemy alembic asyncpg pydantic-settings python-jose[cryptography] passlib[bcrypt] qdrant-client langchain openai pydantic python-multipart
uv add --dev ruff mypy pytest-cov pytest pytest-asyncio httpx pytest-playwright ruff

 uv run mypy app/
