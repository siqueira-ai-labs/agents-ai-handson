"""
cap_05 — Solução Exercício 2: Fallback Explícito para Busca Web
Dificuldade: Médio | Tempo estimado: ~45 min
"""
import os
import json
import pathlib
import pandas as pd
from typing import Annotated, Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict

load_dotenv()

DATA_DIR = pathlib.Path(__file__).parent.parent / "projeto" / "project_data"
RELEVANCE_THRESHOLD = 0.5

llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)


def evaluate_retrieval(docs_with_scores: list) -> bool:
    """Retorna True se os documentos são suficientemente relevantes."""
    if not docs_with_scores:
        return False
    best_score = max(score for _, score in docs_with_scores)
    return best_score >= RELEVANCE_THRESHOLD


def _load_vendas_context() -> str:
    df = pd.read_csv(DATA_DIR / "vendas.csv")
    return df.to_string(index=False)


def _score_relevance(query: str, context: str) -> float:
    """Usa LLM para avaliar relevância query→contexto; retorna float 0-1."""
    prompt = (
        f"Em uma escala de 0.0 a 1.0, qual a probabilidade de a seguinte base de dados "
        f"responder esta pergunta?\n\nPergunta: {query}\n\nBase de dados (primeiras 5 linhas):\n"
        f"{context[:800]}\n\nResponda SOMENTE com um número decimal (ex: 0.85)."
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        return float(response.content.strip())
    except ValueError:
        return 0.0


def _web_search_mock(query: str) -> str:
    """Simula busca web — em produção usar TavilySearchResults."""
    return (
        f"[Resultado da busca web para '{query}']\n"
        "Sem acesso à internet em tempo real, mas aqui está um contexto genérico: "
        "o mercado de tecnologia continua em expansão, com crescimento estimado de 12% ao ano. "
        "Tendências incluem IA generativa, sustentabilidade em hardware e cloud-first."
    )


class State(TypedDict):
    messages: Annotated[list, add_messages]
    query: str
    context: str
    relevance_score: float
    source: str


def retrieve_node(state: State) -> dict:
    query = state.get("query", "")
    if not query and state["messages"]:
        query = state["messages"][-1].content
    context = _load_vendas_context()
    score = _score_relevance(query, context)
    return {"query": query, "context": context, "relevance_score": score}


def route_by_relevance(state: State) -> Literal["generate_from_db", "web_search"]:
    return "generate_from_db" if state["relevance_score"] >= RELEVANCE_THRESHOLD else "web_search"


def generate_from_db_node(state: State) -> dict:
    prompt = f"Com base nos dados abaixo, responda: {state['query']}\n\n{state['context']}"
    response = llm.invoke([SystemMessage(content="Você é um analista de dados."), HumanMessage(content=prompt)])
    return {"messages": [response], "source": "base_interna"}


def web_search_node(state: State) -> dict:
    web_result = _web_search_mock(state["query"])
    response = llm.invoke([
        SystemMessage(content="Você é um assistente de pesquisa."),
        HumanMessage(content=f"Com base na busca web a seguir, responda: {state['query']}\n\n{web_result}"),
    ])
    return {"messages": [response], "source": "busca_web"}


graph = StateGraph(State)
graph.add_node("retrieve", retrieve_node)
graph.add_node("generate_from_db", generate_from_db_node)
graph.add_node("web_search", web_search_node)
graph.set_entry_point("retrieve")
graph.add_conditional_edges("retrieve", route_by_relevance)
graph.add_edge("generate_from_db", END)
graph.add_edge("web_search", END)

app = graph.compile(checkpointer=MemorySaver())


def run_query(query: str, thread_id: str = "cap05-ex02") -> dict:
    config = {"configurable": {"thread_id": thread_id}}
    initial = {
        "messages": [HumanMessage(content=query)],
        "query": query,
        "context": "",
        "relevance_score": 0.0,
        "source": "",
    }
    state = app.invoke(initial, config=config)
    return {
        "resposta": state["messages"][-1].content,
        "fonte": state.get("source", "desconhecida"),
        "score": state.get("relevance_score", 0.0),
    }


if __name__ == "__main__":
    queries = [
        ("Qual foi o faturamento total em 2024?", "cap05-q1"),
        ("Quais são as perspectivas do mercado de IA para 2026?", "cap05-q2"),
    ]
    for q, tid in queries:
        print(f"\n> {q}")
        result = run_query(q, thread_id=tid)
        print(f"Fonte: {result['fonte']} (score={result['score']:.2f})")
        print(f"Resposta: {result['resposta']}")
