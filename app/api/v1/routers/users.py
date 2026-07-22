from sqlalchemy.exc import IntegrityError

from fastapi import APIRouter, Depends, HTTPException

from app.crud.users import create_user, get_user_by_email, update_user
from app.db.session import get_db
from app.schemas.users import UserCreate, UserResponse, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/users", tags=["user"])


@router.post("", status_code=201)
async def create_new_user(
    user_create: UserCreate, session: AsyncSession = Depends(get_db)
) -> UserResponse:
    try:
        user = await create_user(db_session=session, data=user_create)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Email already exists")
    return UserResponse.model_validate(user)


@router.patch("")
async def update_existing_user(
    user_update: UserUpdate, session: AsyncSession = Depends(get_db)
) -> UserResponse:
    user = await get_user_by_email(session, user_update.email)
    if not user:
        raise HTTPException(status_code=404)
    updated = await update_user(session, user, user_update)
    return UserResponse.model_validate(updated)
