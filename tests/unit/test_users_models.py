import pytest

from app.models.users import User


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
