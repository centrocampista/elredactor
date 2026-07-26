import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from app.api.v1.routers.contsants import (
    ALLOWED_TYPES,
    MAX_FILE_SIZE,
    UPLOAD_DIR,
    DocumentStatus,
)
from app.api.v1.routers.dependencies import get_current_credential
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.documents import create_document
from app.db.session import get_db
from app.domain.documents import DocumentData
from app.models.api_credentials import ApiCredential
from app.schemas.documents import DocumentUploadResponse


class UploadValidator:
    def __init__(self, file: UploadFile = File(...)):
        self.file = file

    async def validate(self) -> bytes:
        if self.file.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=415, detail="File has not alloved type.")
        contents = b""
        while chunk := await self.file.read():
            contents += chunk
            if len(contents) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413, detail="Uploaded file is too large."
                )
        return contents


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(get_current_credential)],
)


@router.post("/upload", status_code=201)
async def upload_document(
    validator: UploadValidator = Depends(),
    session: AsyncSession = Depends(get_db),
    current_credential: ApiCredential = Depends(get_current_credential),
) -> DocumentUploadResponse:

    contents = await validator.validate()
    document_id = uuid.uuid4()
    filename = validator.file.filename
    if filename is None:
        raise HTTPException(status_code=422, detail="Filename is required.")
    content_type = validator.file.content_type or ""
    extension = ALLOWED_TYPES[content_type]

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / f"{document_id}{extension}"

    file_path.write_bytes(contents)

    result = await create_document(
        session,
        DocumentData(
            id=document_id,
            user_id=current_credential.user_id,
            filename=filename,
            extension=extension,
            file_path=str(file_path),
            doc_status=DocumentStatus.PENDING,
        ),
    )

    return DocumentUploadResponse(
        id=result.id,
        filename=result.filename,
        extension=result.extension,
        doc_status=result.doc_status,
    )
