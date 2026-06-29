import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from app.api.v1.routers.contsants import ALLOWED_TYPES, MAX_FILE_SIZE, UPLOAD_DIR

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
                raise HTTPException(status_code=413, detail="Uploaded file is too large.")
        return contents

router = APIRouter(prefix='/documents', tags=['documents'])

@router.post('/upload')
async def upload_document(validator: UploadValidator = Depends()):
    contents = await validator.validate()
    document_id = str(uuid.uuid4())
    filename = validator.file.filename
    content_type = validator.file.content_type or ""
    extension = ALLOWED_TYPES[content_type]
    
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / f"{document_id}.{extension}"
    
    file_path.write_bytes(contents)
    
    return {
        "document_id": document_id,
        "filename": filename,
        "extension": extension,
        "status": 'pending',
    }