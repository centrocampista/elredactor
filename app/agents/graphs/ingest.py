import uuid

from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyMuPDFLoader,
    TextLoader,
)
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import END, StateGraph
from qdrant_client.models import PointStruct

from app.agents.state import IngestState
from app.config import settings
from app.db.session import AsyncSessionLocal
from app.models.documents import Document
from app.vector_db.session import qdrant_writer

COLLECTION_NAME = "documents"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

embeddings = OpenAIEmbeddings(
    model=settings.openrouter_embedding_model,
    openai_api_key=settings.openrouter_api_key,
    openai_api_base=settings.openrouter_base_url,
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ".", " "],
)


def get_loader(file_path: str, extension: str):
    loaders = {
        ".pdf": PyMuPDFLoader(file_path),
        ".txt": TextLoader(file_path),
        ".md": TextLoader(file_path),
        ".docx": Docx2txtLoader(file_path),
    }
    return loaders[extension]


async def set_document_status(document_id: str, status: str) -> None:
    async with AsyncSessionLocal() as session:
        doc = await session.get(Document, uuid.UUID(document_id))
        if doc is not None:
            doc.doc_status = status
            await session.commit()


async def ingest_node(state: IngestState) -> dict:
    doc = state["document"]
    document_id: str = doc["id"]

    try:
        await set_document_status(document_id, "processing")

        loader = get_loader(doc["file_path"], doc["extension"])
        documents = loader.load()
        chunks = splitter.split_documents(documents)

        texts = [chunk.page_content for chunk in chunks]
        vectors = await embeddings.aembed_documents(texts)

        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "document_id": document_id,
                    "filename": doc["filename"],
                    "chunk_index": i,
                    "text": texts[i],
                },
            )
            for i, vector in enumerate(vectors)
        ]

        await qdrant_writer.upsert(collection_name=COLLECTION_NAME, points=points)
        await set_document_status(document_id, "done")

        return {"status": "done", "error": None}

    except Exception as e:
        await set_document_status(document_id, "failed")
        return {"status": "failed", "error": str(e)}


builder = StateGraph(IngestState)
builder.add_node("ingest", ingest_node)
builder.set_entry_point("ingest")
builder.add_edge("ingest", END)

graph = builder.compile()
