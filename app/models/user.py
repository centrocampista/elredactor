
import uuid

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    first_name: Mapped[str] = mapped_column(
        String, nullable=False
    )
    last_name: Mapped[str] = mapped_column(
        String, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String, nullable=False, unique=True
    )
     