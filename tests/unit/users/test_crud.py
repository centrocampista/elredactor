import uuid

import pytest

from app.crud.users import create_user, update_user
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate


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
    
@pytest.mark.parametrize(
    "user_update, db_user",
    [
        (
        UserUpdate(first_name="John", last_name="Kowalski", email="jan@example.com"),
        User(id=uuid.uuid4(), first_name="Jan", last_name="Kowalski", email="jan@example.com")
         )
    ],
)
@pytest.mark.unit
async def test_update_user(mock_session, db_user, user_update):
    result = await update_user(mock_session, db_user, user_update)
    mock_session.flush.assert_called_once()
    assert result.first_name == user_update.first_name 
    assert result.last_name == user_update.last_name 
    assert result.email == user_update.email 

@pytest.mark.parametrize(
    "user_update, db_user",
    [
        (
        UserUpdate(first_name="Jan", last_name="Kowalski", email="john@example.com"),
        User(id=uuid.uuid4(), first_name="Jan", last_name="Kowalski", email="jan@example.com")
         )
    ],
)
@pytest.mark.unit
async def test_update_user_skip_new_email(mock_session, db_user, user_update):
    result = await update_user(mock_session, db_user, user_update)
    mock_session.flush.assert_called_once()
    assert result.first_name == user_update.first_name 
    assert result.last_name == user_update.last_name 
    assert result.email == db_user.email 


@pytest.mark.parametrize(
    "user_update, db_user",
    [
        (
        UserUpdate(first_name=None, last_name="Smith", email="jan@example.com"),
        User(id=uuid.uuid4(), first_name='Jan', last_name="Kowalski", email="jan@example.com")
        ),
        (
        UserUpdate(first_name=None, last_name=None, email="jan@example.com"),
        User(id=uuid.uuid4(), first_name='Jan', last_name="Kowalski", email="jan@example.com")
        ),
        (
        UserUpdate(first_name='John', email="jan@example.com"),
        User(id=uuid.uuid4(), first_name='Jan', last_name="Kowalski", email="jan@example.com")
        ),
        (
        UserUpdate(last_name="Smith", email="jan@example.com"),
        User(id=uuid.uuid4(), first_name='Jan', last_name="Kowalski", email="jan@example.com")
        )
    ],
)
@pytest.mark.unit
async def test_update_user_exclude_unset(mock_session, db_user, user_update):
    expected_first_name = user_update.first_name if user_update.first_name else db_user.first_name
    expected_last_name = user_update.last_name if user_update.last_name else db_user.last_name
    result = await update_user(mock_session, db_user, user_update)
    mock_session.flush.assert_called_once()
    assert result.first_name == expected_first_name
    assert result.last_name == expected_last_name
    assert result.email == db_user.email 