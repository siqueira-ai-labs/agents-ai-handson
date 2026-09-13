"""
cap_04 — Solução Exercício 3: Checkpointing Persistente e Auditoria
Dificuldade: Difícil | Tempo estimado: ~2-3h
"""
import os
import sys
import sqlite3
import pathlib
from typing import Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

load_dotenv()

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))
from finance_bot import get_stock_price, calculate_return  # noqa: E402

DB_PATH = str(pathlib.Path(__file__).parent.parent / "checkpoints.db")


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)

tools = [get_stock_price, calculate_return]
llm_with_tools = llm.bind_tools(tools)


def agent_node(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


def build_app(db_path: str):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    graph = StateGraph(State)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile(checkpointer=checkpointer), checkpointer


def list_sessions(db_path: str) -> list[str]:
    """Lista todos os thread_ids com checkpoints salvos."""
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute(
            "SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id"
        )
        return [row[0] for row in cur.fetchall()]
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


def get_session_history(db_path: str, thread_id: str) -> list:
    """Retorna snapshots de estado de uma sessão via get_state_history."""
    app, _ = build_app(db_path)
    config = {"configurable": {"thread_id": thread_id}}
    return list(app.get_state_history(config))


def print_audit_report(db_path: str):
    """Exibe relatório de auditoria de todas as sessões."""
    sessions = list_sessions(db_path)
    if not sessions:
        print("Nenhuma sessão encontrada.")
        return

    for thread_id in sessions:
        history = get_session_history(db_path, thread_id)
        print(f"\n[Sessão: {thread_id}] — {len(history)} snapshots")
        for snap in history:
            msgs = snap.values.get("messages", [])
            tools_used = [
                m.tool_calls[0]["name"]
                for m in msgs
                if isinstance(m, AIMessage) and hasattr(m, "tool_calls") and m.tool_calls
            ]
            ts = snap.metadata.get("created_at", "N/A") if snap.metadata else "N/A"
            print(f"  ts={ts} | msgs={len(msgs)} | ferramentas={tools_used or '—'}")


if __name__ == "__main__":
    app, _ = build_app(DB_PATH)
    config = {"configurable": {"thread_id": "auditoria-sessao-1"}}

    queries = [
        "Qual a cotação de PETR4.SA?",
        "Calcule o retorno entre R$30 e R$38.",
    ]
    for q in queries:
        print(f"\n> {q}")
        state = app.invoke({"messages": [("human", q)]}, config=config)
        print(f"Bot: {state['messages'][-1].content}")

    print("\n" + "=" * 50)
    print("RELATÓRIO DE AUDITORIA")
    print("=" * 50)
    print_audit_report(DB_PATH)
