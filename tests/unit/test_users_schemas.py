from pydantic import ValidationError
import pytest

from app.schemas.users import UserCreate


@pytest.mark.unit
def test_user_create_valid():
    user = UserCreate(first_name="Jan", last_name="Kowalski", email="jan@example.com")
    assert user.email == "jan@example.com"


@pytest.mark.unit
def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(first_name="Jan", last_name="Kowalski", email="not-email")


@pytest.mark.unit
def test_user_create_missing_field():
    with pytest.raises(ValidationError):
        UserCreate(first_name="Jan", email="jan@example.com")
