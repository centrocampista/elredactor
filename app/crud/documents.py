from dataclasses import asdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.documents import DocumentData
from app.models.documents import Document


async def create_document(
    db_session: AsyncSession, document_data: DocumentData
) -> Document:
    document = Document(**asdict(document_data))
    db_session.add(document)
    await db_session.flush()
    await db_session.refresh(document)
    return document
