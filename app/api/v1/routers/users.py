
from fastapi import APIRouter, Depends, HTTPException

from app.crud.users import create_user, update_user
from app.db.session import get_db
from app.schemas.users import UserCreate, UserResponse, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix='/users', tags=['user'])

@router.post
async def create_new_user(user_create: UserCreate, session: AsyncSession = Depends(get_db)) -> UserResponse:
    user = await create_user(db_session=session, data=user_create)
    return UserResponse.model_validate(user)

@router.patch
async def update_existing_user(user_update: UserUpdate, session: AsyncSession = Depends(get_db)) -> UserResponse:
    user = await get_user_by_email(session, user_update.email)
    if not user:
        raise HTTPException(status_code=404)
    updated = await update_user(session, user, user_update)