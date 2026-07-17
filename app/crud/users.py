
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import User
from app.schemas.users import UserCreate, UserUpdate


async def create_user(db_session: AsyncSession, data: UserCreate) -> User:
    user = User(**data.model_dump())
    db_session.add(user)
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

async def get_user_by_email(db_session: AsyncSession, email: str) -> User | None:
    result = await db_session.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()