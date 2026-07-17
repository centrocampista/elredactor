from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.config import settings
from app.db.session import engine, get_db
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport


@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)


@pytest.fixture(scope="module")
def test_settings():
    return settings


@pytest.fixture(scope="function")
async def db_session():

    async with engine.connect() as connection:
        await connection.begin()

        async_session = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        async with async_session() as session:
            yield session

        await connection.rollback()


@pytest.fixture(scope="function")
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_httpx(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    app.dependency_overrides.clear()