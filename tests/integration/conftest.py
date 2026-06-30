from typing import NamedTuple

from fastapi.testclient import TestClient
import pytest
from app.main import app


@pytest.fixture(scope='module')
def test_client():
    return TestClient(app)

class SettingsMock(NamedTuple):
    environment: str
    is_dev: bool
    is_staging: bool
    is_prod: bool
    debug: bool