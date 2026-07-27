from dataclasses import asdict

import httpx
from fastapi import HTTPException

from app.config import settings
from app.domain.documents import DocumentData


async def trigger_ingest(document_data: DocumentData) -> str:
    async with httpx.AsyncClient(timeout=5.0) as client:
        thread_response = await client.post(f"{settings.langgraph_url}/threads")
        if thread_response.status_code != 200:
            raise HTTPException(
                status_code=502, detail="Failed to create LangGraph thread"
            )
        thread_id: str = thread_response.json()["thread_id"]

        run_response = await client.post(
            f"{settings.langgraph_url}/threads/{thread_id}/runs",
            json={
                "assistant_id": "ingest",
                "input": {"document": asdict(document_data)},
            },
        )
        if run_response.status_code != 200:
            raise HTTPException(
                status_code=502, detail="Failed to start LangGraph ingest run"
            )

    return thread_id
