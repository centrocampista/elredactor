from dataclasses import dataclass
import uuid

from app.api.v1.routers.contsants import DocumentStatus


@dataclass
class DocumentData:
    id: uuid.UUID
    user_id: uuid.UUID
    filename: str
    extension: str
    file_path: str
    doc_status: DocumentStatus
