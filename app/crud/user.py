
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate


async def create_user(db_session: AsyncSession, data: UserCreate) -> User:
    user = User(**data.model_dump)
    await db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user