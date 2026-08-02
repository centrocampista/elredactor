import json
from dataclasses import asdict

import httpx
from fastapi import HTTPException

from app.config import settings
from app.domain.documents import DocumentData


def _to_json_safe(data: dict) -> dict:
    return json.loads(json.dumps(data, default=str))


async def trigger_ingest(document_data: DocumentData) -> str:
    async with httpx.AsyncClient(timeout=5.0) as client:
        thread_response = await client.post(
            f"{settings.langgraph_url}/threads", json={}
        )
        if not thread_response.is_success:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to create LangGraph thread: {thread_response.status_code}",
            )
        thread_id: str = thread_response.json()["thread_id"]

        run_response = await client.post(
            f"{settings.langgraph_url}/threads/{thread_id}/runs",
            json={
                "assistant_id": "ingest",
                "input": {"document": _to_json_safe(asdict(document_data))},
            },
        )
        if not run_response.is_success:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to start LangGraph ingest run: {run_response.status_code}",
            )

    return thread_id
