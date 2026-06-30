from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.config import settings

@pytest.fixture(scope='module')
def test_client():
    return TestClient(app)

@pytest.fixture(scope='module')
def test_settings():
    return settings