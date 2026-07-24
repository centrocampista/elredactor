from passlib.hash import bcrypt
from sqlalchemy import select

from app.domain.api_credentials import ApiCredentialResponse
from app.models.api_credentials import ApiCredential
from sqlalchemy.ext.asyncio import AsyncSession
import secrets
from app.models.users import User


async def verify_api_credential(
    db_session: AsyncSession, api_key: str, api_secret: str
) -> ApiCredential | None:
    result = await db_session.execute(
        select(ApiCredential).where(ApiCredential.key == api_key)
    )
    credential = result.scalar_one_or_none()
    if credential is None:
        return None
    if not bcrypt.verify(api_secret, credential.secret_hash):
        return None
    return credential


async def create_api_credential(
    db_session: AsyncSession, email: str
) -> ApiCredentialResponse | None:
    users = await db_session.execute(select(User).where(User.email == email))
    user = users.scalar_one_or_none()
    if user is None:
        return None

    key = secrets.token_urlsafe(32)
    secret = secrets.token_urlsafe(32)
    secret_hash = bcrypt.hash(secret)

    credential = ApiCredential(user_id=user.id, key=key, secret_hash=secret_hash)
    db_session.add(credential)
    await db_session.flush()
    await db_session.refresh(credential)

    return ApiCredentialResponse(
        user_id=user.id,
        email=email,
        key=key,
        secret=secret,
        credential_id=credential.id,
    )
