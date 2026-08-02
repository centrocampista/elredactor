from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


class IngestState(TypedDict):
    document: dict  # DocumentData serialized via asdict()
    status: str  # pending → processing → done / failed
    error: str | None
