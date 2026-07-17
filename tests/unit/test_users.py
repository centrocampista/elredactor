from pydantic import ValidationError
import pytest

from app.crud.users import create_user
from app.models.users import User
from app.schemas.users import UserCreate


@pytest.mark.unit
def test_user_has_email_column():
    col = User.__table__.columns["email"]
    assert col is not None


@pytest.mark.unit
def test_user_email_is_unique():
    col = User.__table__.columns["email"]
    assert col.unique is True


@pytest.mark.unit
def test_user_id_is_primey_key():
    col = User.__table__.columns["id"]
    assert col.primary_key is True


# first_name="Jan", last_name="Kowalski", email="jan@example.com"


@pytest.mark.unit
@pytest.mark.parametrize(
    "user_create",
    (UserCreate(first_name="Jan", last_name="Kowalski", email="jan@example.com")),
)
async def test_create_user(mock_session, user_create):
    user = await create_user(mock_session)
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    assert user.email == user_create.email


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
