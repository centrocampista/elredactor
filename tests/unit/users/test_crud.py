import pytest

from app.crud.users import create_user
from app.schemas.users import UserCreate


@pytest.mark.parametrize(
    "user_create",
    [
        UserCreate(first_name="Jan", last_name="Kowalski", email="jan@example.com"),
    ],
)
@pytest.mark.unit
async def test_create_user(mock_session, user_create):
    user = await create_user(mock_session, user_create)
    mock_session.add.assert_called_once()
    mock_session.flush.assert_called_once()
    assert user.email == user_create.email
