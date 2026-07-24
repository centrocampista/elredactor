import uuid

from pydantic import BaseModel, EmailStr


class ApiCredentialCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str


class ApiCredentialSchema(BaseModel):
    user_id: uuid.UUID
    email: EmailStr
    key: str
    secret: str
    credential_id: uuid.UUID
