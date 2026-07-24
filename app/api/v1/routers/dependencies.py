from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.api_credentials import verify_api_credential
from app.db.session import get_db
from app.models.api_credentials import ApiCredential


async def get_current_credential(
    api_key: str = Header(..., alias="X-Api-Key"),
    api_secret: str = Header(..., alias="X-Api-Secret"),
    session: AsyncSession = Depends(get_db),
) -> ApiCredential:

    credential = await verify_api_credential(session, api_key, api_secret)
    if credential is None:
        raise HTTPException(status_code=401, detail="Unauthorized user")
    return credential
