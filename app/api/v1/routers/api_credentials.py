from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.routers.dependencies import get_current_credential
from app.crud.api_credentials import create_api_credential
from app.db.session import get_db
from app.schemas.api_credentials import ApiCredentialCreate, ApiCredentialSchema
from dataclasses import asdict


router = APIRouter(
    prefix="/api-creds",
    tags=["api-creds"],
    dependencies=[Depends(get_current_credential)],
)


@router.post("", status_code=201)
async def create_new_api_credential(
    data: ApiCredentialCreate, session: AsyncSession = Depends(get_db)
) -> ApiCredentialSchema:
    result = await create_api_credential(session, data.email)
    if result is None:
        raise HTTPException(status_code=404, detail="User was not found")
    return ApiCredentialSchema(**asdict(result))
