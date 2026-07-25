from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from app.agents.state import AgentState
from app.config import settings

llm = ChatOpenAI(
    base_url=settings.openrouter_base_url,
    api_key=settings.openrouter_api_key,
    model=settings.openrouter_model,
)


async def call_llm(state: AgentState) -> dict:
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}


async def summarize(state: AgentState) -> dict:
    last = state["messages"][-1].content
    summary = await llm.ainvoke(
        [{"role": "user", "content": f"Podsumuj w jednym zdaniu: {last}"}]
    )
    return {"messages": [summary]}


builder = StateGraph(AgentState)
builder.add_node("llm", call_llm)
builder.add_node("summarize", summarize)
builder.set_entry_point("llm")
builder.add_edge("llm", "summarize")
builder.add_edge("summarize", END)

graph = builder.compile()
