import uuid

from pydantic import BaseModel

from app.api.v1.routers.contsants import DocumentStatus


class DocumentUploadResponse(BaseModel):
    id: uuid.UUID
    filename: str
    extension: str
    doc_status: DocumentStatus
    langgraph_thread_id: str | None = None
