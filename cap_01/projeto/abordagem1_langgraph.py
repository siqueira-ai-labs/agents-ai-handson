"""
cap_01 — Abordagem 1: Agente de Pesquisa com LangGraph
Módulo 2: Fundamentos da IA Agentiva

Provider: OpenRouter (openrouter.ai)
Modelo: nvidia/llama-3.1-nemotron-70b-instruct:free
"""
import os
from typing import List, TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

load_dotenv()

# --- Estado do grafo ---
class AgentState(TypedDict):
    task: str
    search_results: List[str]
    report: str


# --- LLM via OpenRouter ---
model_name = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")
llm = ChatOpenAI(
    model=model_name,
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# --- Ferramenta de busca ---
search_tool = TavilySearchResults(max_results=3)

# --- Agente de pesquisa ---
prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um pesquisador especializado. Use as ferramentas disponíveis."),
    ("human", "{task}"),
    ("placeholder", "{agent_scratchpad}"),
])
agent = create_tool_calling_agent(llm, [search_tool], prompt)
agent_executor = AgentExecutor(agent=agent, tools=[search_tool], verbose=True)


# --- Nós do grafo ---
def research_agent_node(state: AgentState):
    result = agent_executor.invoke({"task": state["task"]})
    return {"search_results": [result["output"]]}


def report_writer_node(state: AgentState):
    context = "\n".join(state["search_results"])
    report_prompt = f"Com base no seguinte contexto, escreva um relatório conciso:\n\n{context}"
    response = llm.invoke(report_prompt)
    return {"report": response.content}


# --- Construção do grafo ---
def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("research", research_agent_node)
    graph.add_node("write_report", report_writer_node)
    graph.set_entry_point("research")
    graph.add_edge("research", "write_report")
    graph.add_edge("write_report", END)
    return graph.compile()


if __name__ == "__main__":
    app = build_graph()
    result = app.invoke({"task": "Quais são as principais tendências de IA Agentiva em 2025?"})
    print("\n### Relatório Final ###")
    print(result["report"])
