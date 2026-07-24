import uuid

from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import AccessTrackingMixin


class ApiCredential(Base, AccessTrackingMixin):
    __tablename__ = "api_credentials"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )
    key: Mapped[str] = mapped_column(String, nullable=False, index=True, unique=True)
    secret_hash: Mapped[str] = mapped_column(String, nullable=False)
