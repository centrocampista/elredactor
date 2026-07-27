import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.v1.routers.dependencies import get_current_credential
from app.config import settings
from app.models.api_credentials import ApiCredential


class AskRequest(BaseModel):
    question: str
    thread_id: str | None = None


class AskResponse(BaseModel):
    thread_id: str
    answer: str


router = APIRouter(
    prefix="/agent",
    tags=["agent"],
    dependencies=[Depends(get_current_credential)],
)


@router.post("/ask")
async def ask(
    body: AskRequest,
    current_credential: ApiCredential = Depends(get_current_credential),
) -> AskResponse:
    async with httpx.AsyncClient(timeout=60.0) as client:
        thread_id = body.thread_id

        if thread_id is None:
            thread_response = await client.post(f"{settings.langgraph_url}/threads")
            if thread_response.status_code != 200:
                raise HTTPException(
                    status_code=502, detail="Failed to create LangGraph thread"
                )
            thread_id = thread_response.json()["thread_id"]

        response = await client.post(
            f"{settings.langgraph_url}/threads/{thread_id}/runs/wait",
            json={
                "assistant_id": "researcher",
                "input": {"messages": [{"role": "user", "content": body.question}]},
            },
        )
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="LangGraph run failed")

    result = response.json()
    try:
        answer = result["values"]["messages"][-1]["content"]
    except (KeyError, IndexError):
        raise HTTPException(
            status_code=502, detail="Unexpected LangGraph response shape"
        )

    return AskResponse(thread_id=thread_id, answer=answer)
