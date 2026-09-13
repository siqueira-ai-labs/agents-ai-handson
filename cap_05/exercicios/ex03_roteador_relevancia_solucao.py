"""
cap_05 — Solução Exercício 3: Roteador com Avaliação de Relevância
Dificuldade: Difícil | Tempo estimado: ~2-3h
"""
import os
import json
import pathlib
import pandas as pd
from typing import Annotated, Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict

load_dotenv()

DATA_DIR = pathlib.Path(__file__).parent.parent / "projeto" / "project_data"
CONFIDENCE_THRESHOLD = 0.7

llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)


class RoutingDecision(BaseModel):
    tool: str = Field(description="Nome da ferramenta mais adequada")
    confidence: float = Field(description="Confiança de 0.0 a 1.0", ge=0.0, le=1.0)
    reasoning: str = Field(description="Justificativa em uma linha")


TOOLS_DESCRIPTION = {
    "consultar_vendas": "Dados de vendas: faturamento, quantidades, vendedores, regiões, períodos",
    "consultar_produtos": "Catálogo de produtos: preços, estoque, categorias, fornecedores",
    "consultar_devolucoes": "Dados de devoluções: motivos, taxas de devolução, produtos devolvidos",
    "busca_web": "Informações externas: tendências de mercado, notícias, dados macroeconômicos",
}

routing_llm = llm.with_structured_output(RoutingDecision)
routing_log: list[dict] = []


def judge_routing(query: str) -> RoutingDecision:
    tools_desc = "\n".join(f"- {k}: {v}" for k, v in TOOLS_DESCRIPTION.items())
    prompt = (
        f"Você é um roteador de ferramentas. Analise a query e escolha a ferramenta mais adequada.\n\n"
        f"Ferramentas disponíveis:\n{tools_desc}\n\n"
        f"Query: {query}\n\n"
        f"Retorne: tool (nome exato), confidence (0.0-1.0), reasoning (uma linha)."
    )
    return routing_llm.invoke([HumanMessage(content=prompt)])


def _load_data(tool: str) -> str:
    if tool == "consultar_vendas":
        df = pd.read_csv(DATA_DIR / "vendas.csv")
        return df.to_string(index=False)
    elif tool == "consultar_produtos":
        df = pd.read_csv(DATA_DIR / "produtos.csv")
        return df.to_string(index=False)
    elif tool == "consultar_devolucoes":
        with open(DATA_DIR / "devolucoes.json", encoding="utf-8") as f:
            return pd.DataFrame(json.load(f)).to_string(index=False)
    return ""


class State(TypedDict):
    messages: Annotated[list, add_messages]
    query: str
    routing_decision: dict
    context: str


def router_node(state: State) -> dict:
    query = state.get("query") or state["messages"][-1].content
    decision = judge_routing(query)
    routing_log.append({
        "query": query,
        "tool": decision.tool,
        "confidence": decision.confidence,
        "reasoning": decision.reasoning,
    })
    return {"query": query, "routing_decision": decision.model_dump()}


def route_after_judge(state: State) -> Literal["execute_tool", "fallback"]:
    confidence = state["routing_decision"].get("confidence", 0)
    return "execute_tool" if confidence >= CONFIDENCE_THRESHOLD else "fallback"


def execute_tool_node(state: State) -> dict:
    tool = state["routing_decision"]["tool"]
    if tool == "busca_web":
        context = f"[Busca web simulada para: {state['query']}] Informações de mercado não disponíveis localmente."
    else:
        context = _load_data(tool)
    return {"context": context}


def fallback_node(state: State) -> dict:
    context = f"Confiança insuficiente ({state['routing_decision']['confidence']:.2f}). Usando base de vendas como padrão."
    context += "\n\n" + _load_data("consultar_vendas")
    return {"context": context}


def generate_node(state: State) -> dict:
    decision = state["routing_decision"]
    prompt = (
        f"Usando os dados abaixo (fonte: {decision['tool']}), responda: {state['query']}\n\n"
        f"{state['context'][:3000]}"
    )
    response = llm.invoke([
        SystemMessage(content="Você é um analista de negócios especializado."),
        HumanMessage(content=prompt),
    ])
    return {"messages": [response]}


graph = StateGraph(State)
graph.add_node("router", router_node)
graph.add_node("execute_tool", execute_tool_node)
graph.add_node("fallback", fallback_node)
graph.add_node("generate", generate_node)
graph.set_entry_point("router")
graph.add_conditional_edges("router", route_after_judge)
graph.add_edge("execute_tool", "generate")
graph.add_edge("fallback", "generate")
graph.add_edge("generate", END)

app = graph.compile(checkpointer=MemorySaver())


def run_query(query: str, thread_id: str = "cap05-ex03") -> dict:
    config = {"configurable": {"thread_id": thread_id}}
    initial: State = {
        "messages": [HumanMessage(content=query)],
        "query": query,
        "routing_decision": {},
        "context": "",
    }
    state = app.invoke(initial, config=config)
    decision = state.get("routing_decision", {})
    return {
        "resposta": state["messages"][-1].content,
        "tool": decision.get("tool"),
        "confidence": decision.get("confidence"),
        "reasoning": decision.get("reasoning"),
    }


if __name__ == "__main__":
    queries = [
        "Qual foi o faturamento do Q3 de 2024?",
        "Quais são as tendências de mercado para 2026?",
        "Quantos produtos foram devolvidos em março?",
    ]
    for q in queries:
        print(f"\nQuery: {q}")
        result = run_query(q, thread_id=f"cap05-r{hash(q)}")
        print(f"  → ferramenta: {result['tool']} (conf={result['confidence']:.2f})")
        print(f"  → razão: {result['reasoning']}")
        print(f"  → resposta: {result['resposta'][:200]}...")

    print("\n\n=== LOG DE ROTEAMENTO ===")
    for entry in routing_log:
        print(f"  [{entry['tool']}|{entry['confidence']:.2f}] {entry['query'][:60]}")
