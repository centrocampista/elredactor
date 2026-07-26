import uuid

from pydantic import BaseModel, EmailStr


class ApiCredentialCreate(BaseModel):
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None


class ApiCredentialSchema(BaseModel):
    user_id: uuid.UUID
    email: EmailStr
    key: str
    secret: str
    credential_id: uuid.UUID
