import uuid

from fastapi.testclient import TestClient
import pytest
from app.api.v1.routers.dependencies import get_current_credential
from app.main import app
from app.config import settings
from app.db.session import get_db
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from httpx import AsyncClient, ASGITransport

from app.models.api_credentials import ApiCredential
from app.models.users import User

test_engine = create_async_engine(
    settings.database_url,
    poolclass=NullPool,
)


@pytest.fixture(scope="module")
def test_settings():
    return settings


@pytest.fixture(scope="function")
async def db_session():

    async with test_engine.connect() as connection:
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
async def db_user(db_session) -> User:
    user = User(
        id=uuid.uuid4(),
        first_name="Test",
        last_name="User",
        email=f"test-{uuid.uuid4()}@example.com",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture(scope="function")
def client_fastapi(db_session, db_user):
    async def override_get_db():
        yield db_session

    async def override_get_current_credential() -> ApiCredential:
        return ApiCredential(
            id=uuid.uuid4(), user_id=db_user.id, key="test-key", secret_hash="x"
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_credential] = override_get_current_credential
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def client_httpx(db_session, db_user):
    async def override_get_db():
        yield db_session

    async def override_get_current_credential() -> ApiCredential:
        return ApiCredential(
            id=uuid.uuid4(), user_id=db_user.id, key="test-key", secret_hash="x"
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_credential] = override_get_current_credential
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    app.dependency_overrides.clear()


@pytest.fixture
def sample_pdf() -> bytes:
    return b"%PDF-1.4 1 0 obj<</Type/Catalog>>endobj"


@pytest.fixture
def sample_txt() -> bytes:
    return b"plain text file"


@pytest.fixture
def sample_md() -> bytes:
    return b"# Md heading"


@pytest.fixture
def sample_docx() -> bytes:
    return b"PK\x03\x04"  # zip file signature
