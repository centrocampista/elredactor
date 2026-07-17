from unittest.mock import AsyncMock, MagicMock
import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_page():
    return MagicMock()


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    return session
