"""
cap_14 — Alternativa 100% Local: PostgresRedisSaver via Ollama
Mesma arquitetura de projeto/exemplo_uso.py, trocando o LLM de OpenRouter
por Ollama local. PostgreSQL e Redis continuam via Docker
(docker compose -f cap_14/docker-compose.yml up -d) — só o LLM é local.

Modelo: qwen3.5:7b
"""
import asyncio
import os
import pathlib
import sys
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))
from postgres_redis_saver import PostgresRedisSaver  # noqa: E402

load_dotenv()

DB_URI = os.getenv("DATABASE_URL", "postgresql://postgres:secret@localhost:5432/langgraph")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class ConversationState(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatOllama(model="qwen3.5:7b", base_url="http://localhost:11434", temperature=0)


def chat_node(state: ConversationState) -> dict:
    return {"messages": [llm.invoke(state["messages"])]}


workflow = StateGraph(ConversationState)
workflow.add_node("chat", chat_node)
workflow.set_entry_point("chat")
workflow.add_edge("chat", END)


async def run_with_persistence(thread_id: str = "sessao-local-42"):
    async with PostgresRedisSaver.from_conn_strings(DB_URI, REDIS_URL) as checkpointer:
        app = workflow.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": thread_id}}

        r1 = await app.ainvoke({"messages": [HumanMessage("Olá! Quem é você?")]}, config=config)
        print("R1:", r1["messages"][-1].content)

        r2 = await app.ainvoke({"messages": [HumanMessage("O que falamos antes?")]}, config=config)
        print("R2:", r2["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(run_with_persistence())
