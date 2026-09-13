"""
cap_05 — Alternativa 100% Local: Agente de Pesquisa de Mercado via Ollama
Mesma arquitetura de projeto/pesquisa_mercado_cohere.py (grafo LangGraph de
2 agentes: Pesquisador -> Analista), trocando Cohere por Ollama e Tavily
(precisa de API key) por DuckDuckGo (busca gratuita, sem key).

Modelo: qwen3.5:7b
"""
from typing import List, TypedDict

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph


class ResearchState(TypedDict):
    task: str
    topic: str
    search_results: List[dict]
    report: str


llm = ChatOllama(model="qwen3.5:7b", base_url="http://localhost:11434", temperature=0)
search_tool = DuckDuckGoSearchRun()


def researcher_node(state: ResearchState) -> dict:
    """Busca na web informações relevantes para a tarefa."""
    texto = search_tool.invoke(state["task"])
    return {"search_results": [{"content": texto}]}


def analyst_node(state: ResearchState) -> dict:
    """Sintetiza os resultados de busca em um relatório."""
    trechos = "\n".join(f"- {r['content']}" for r in state["search_results"] if r.get("content"))
    prompt = (
        f"Com base nas informações de pesquisa abaixo, escreva um relatório "
        f"detalhado sobre '{state['topic']}'.\n\nInformações:\n{trechos}\n\nRelatório:"
    )
    resposta = llm.invoke([HumanMessage(content=prompt)])
    return {"report": resposta.content}


workflow = StateGraph(ResearchState)
workflow.add_node("pesquisador", researcher_node)
workflow.add_node("analista", analyst_node)
workflow.set_entry_point("pesquisador")
workflow.add_edge("pesquisador", "analista")
workflow.add_edge("analista", END)
app = workflow.compile()


def run_research(topic: str) -> str:
    task = f"Realize uma pesquisa de mercado detalhada sobre {topic}"
    final_state = app.invoke({"task": task, "topic": topic, "search_results": [], "report": ""})
    return final_state["report"]


if __name__ == "__main__":
    print(run_research("O futuro do RAG Agentivo na indústria de IA"))
