
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def create_user(db_session: AsyncSession, data: UserCreate) -> User:
    user = User(**data.model_dump)
    await db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user

async def update_user(db_session: AsyncSession, user: User, data: UserUpdate) -> User:
    changes = data.model_dump(exclude_unset=True)
    changes.pop('email')
    for k, v in changes.items():
        setattr(user, k, v)
    await db_session.flush()
    await db_session.refresh(user)
    return user