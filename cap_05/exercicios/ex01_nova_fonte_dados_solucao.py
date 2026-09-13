"""
cap_05 — Solução Exercício 1: Adicionando uma Nova Fonte de Dados
Dificuldade: Fácil | Tempo estimado: ~20 min
"""
import os
import json
import pathlib
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

load_dotenv()

DATA_DIR = pathlib.Path(__file__).parent.parent / "projeto" / "project_data"
VENDAS_PATH = DATA_DIR / "vendas.csv"
PRODUTOS_PATH = DATA_DIR / "produtos.csv"
DEVOLUCOES_PATH = DATA_DIR / "devolucoes.json"

llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)


@tool
def consultar_vendas(query: str) -> str:
    """Consulta dados de vendas (CSV). Use para perguntas sobre faturamento, quantidades vendidas, vendedores e regiões."""
    df = pd.read_csv(VENDAS_PATH)
    return f"Dados de vendas ({len(df)} registros):\n{df.to_string(index=False)}\n\nPergunta: {query}"


@tool
def consultar_produtos(query: str) -> str:
    """Consulta catálogo de produtos (CSV). Use para perguntas sobre estoque, preços e fornecedores."""
    df = pd.read_csv(PRODUTOS_PATH)
    return f"Catálogo de produtos ({len(df)} registros):\n{df.to_string(index=False)}\n\nPergunta: {query}"


@tool
def consultar_devolucoes(query: str) -> str:
    """Consulta dados de devoluções (JSON). Use para perguntas sobre devoluções, motivos e taxas de devolução."""
    with open(DEVOLUCOES_PATH, encoding="utf-8") as f:
        devolucoes = json.load(f)
    df = pd.DataFrame(devolucoes)
    return f"Dados de devoluções ({len(df)} registros):\n{df.to_string(index=False)}\n\nPergunta: {query}"


tools = [consultar_vendas, consultar_produtos, consultar_devolucoes]
llm_with_tools = llm.bind_tools(tools)

from typing import Annotated
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict
from langchain_core.messages import AIMessage


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent_node(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")

app = graph.compile(checkpointer=MemorySaver())


def run_query(query: str, thread_id: str = "cap05-ex01") -> str:
    config = {"configurable": {"thread_id": thread_id}}
    state = app.invoke({"messages": [("human", query)]}, config=config)
    return state["messages"][-1].content


if __name__ == "__main__":
    queries = [
        "Qual produto teve maior taxa de devolução em relação às vendas?",
        "Qual categoria tem mais devoluções?",
        "Qual o faturamento total do ano de 2024?",
    ]
    for q in queries:
        print(f"\n> {q}")
        print(run_query(q, thread_id=f"cap05-{hash(q)}"))
