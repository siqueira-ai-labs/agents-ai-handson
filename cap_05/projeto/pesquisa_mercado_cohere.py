"""
cap_05 — Agente de Pesquisa de Mercado com Cohere + LangGraph
Módulo 6: RAG Agentivo (Agentic RAG)

Time de 2 agentes em um grafo de estado: o Pesquisador busca informações na
web (Tavily) sobre um tópico, e o Analista sintetiza os achados em um
relatório coeso usando o Command da Cohere.
"""
import os
from typing import List, TypedDict

from dotenv import load_dotenv
from langchain_cohere.chat_models import ChatCohere
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

load_dotenv()


class ResearchState(TypedDict):
    task: str
    topic: str
    search_results: List[dict]
    report: str


def build_llm() -> ChatCohere:
    return ChatCohere(
        model=os.getenv("COHERE_MODEL", "command-r-plus"),
        cohere_api_key=os.getenv("COHERE_API_KEY"),
        temperature=0,
    )


def researcher_node(state: ResearchState) -> dict:
    """Busca na web informações relevantes para a tarefa."""
    search_tool = TavilySearchResults(max_results=5)
    resultados = search_tool.invoke(state["task"])
    return {"search_results": resultados if isinstance(resultados, list) else []}


def build_analyst_node(llm: ChatCohere):
    def analyst_node(state: ResearchState) -> dict:
        """Sintetiza os resultados de busca em um relatório."""
        # TavilySearchResults retorna dicts com as chaves 'url' e 'content'.
        trechos = "\n".join(f"- {r['content']}" for r in state["search_results"] if r.get("content"))
        prompt = (
            f"Com base nas informações de pesquisa abaixo, escreva um relatório "
            f"detalhado sobre '{state['topic']}'.\n\nInformações:\n{trechos}\n\nRelatório:"
        )
        resposta = llm.invoke([HumanMessage(content=prompt)])
        return {"report": resposta.content}

    return analyst_node


def build_graph() -> StateGraph:
    llm = build_llm()
    workflow = StateGraph(ResearchState)
    workflow.add_node("pesquisador", researcher_node)
    workflow.add_node("analista", build_analyst_node(llm))
    workflow.set_entry_point("pesquisador")
    workflow.add_edge("pesquisador", "analista")
    workflow.add_edge("analista", END)
    return workflow.compile()


def run_research(topic: str) -> str:
    app = build_graph()
    task = f"Realize uma pesquisa de mercado detalhada sobre {topic}"
    final_state = app.invoke({"task": task, "topic": topic, "search_results": [], "report": ""})
    return final_state["report"]


if __name__ == "__main__":
    print("Agente de Pesquisa de Mercado — digite 'sair' para encerrar\n")
    while True:
        topico = input("Tópico de pesquisa: ").strip()
        if topico.lower() == "sair":
            break
        print(f"\nPesquisando sobre: {topico}...\n")
        print(f"--- RELATÓRIO FINAL ---\n{run_research(topico)}\n")
