from dataclasses import dataclass
import uuid


@dataclass
class ApiCredentialResponse:
    user_id: uuid.UUID
    key: str
    secret: str
    credential_id: uuid.UUID
