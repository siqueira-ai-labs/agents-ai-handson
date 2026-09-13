"""
cap_14 — Exemplo de uso do PostgresRedisSaver
Módulo 15: Gerenciamento de Estado Distribuído em Produção

Requer PostgreSQL e Redis rodando (docker compose -f cap_14/docker-compose.yml up -d).
"""
import asyncio
import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

from postgres_redis_saver import PostgresRedisSaver

load_dotenv()

DB_URI = os.getenv(
    "DATABASE_URL", "postgresql://postgres:secret@localhost:5432/langgraph"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class ConversationState(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)


def chat_node(state: ConversationState) -> dict:
    return {"messages": [llm.invoke(state["messages"])]}


workflow = StateGraph(ConversationState)
workflow.add_node("chat", chat_node)
workflow.set_entry_point("chat")
workflow.add_edge("chat", END)


async def run_with_persistence(thread_id: str = "sessao-42"):
    async with PostgresRedisSaver.from_conn_strings(DB_URI, REDIS_URL) as checkpointer:
        app = workflow.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": thread_id}}

        r1 = await app.ainvoke({"messages": [HumanMessage("Olá! Quem é você?")]}, config=config)
        print("R1:", r1["messages"][-1].content)

        # Turno 2 — retoma o estado anterior automaticamente (mesmo thread_id)
        r2 = await app.ainvoke({"messages": [HumanMessage("O que falamos antes?")]}, config=config)
        print("R2:", r2["messages"][-1].content)

        estado_final = await checkpointer.aget_tuple(config)
        if estado_final:
            print(f"\nÚltimo checkpoint recuperado: {len(estado_final.checkpoint['channel_values']['messages'])} mensagens")


if __name__ == "__main__":
    asyncio.run(run_with_persistence())
