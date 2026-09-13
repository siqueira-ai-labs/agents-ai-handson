"""
cap_01 — Alternativa 100% Local: LangGraph + Ollama (sem API)
Modelo: llama4.1:8b ou qwen3.5:7b

Setup:
    curl -fsSL https://ollama.com/install.sh | sh
    ollama pull llama4.1:8b
    pip install langchain-ollama langchain-community langgraph duckduckgo-search
"""
from typing import List, TypedDict
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END


class AgentState(TypedDict):
    task: str
    search_results: List[str]
    report: str


# qwen3.5:7b tem melhor suporte a function calling que llama4.1:8b
llm = ChatOllama(model="qwen3.5:7b", temperature=0, base_url="http://localhost:11434")
search_tool = DuckDuckGoSearchRun()

prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um pesquisador. Use as ferramentas disponíveis."),
    ("human", "{task}"),
    ("placeholder", "{agent_scratchpad}"),
])
agent = create_tool_calling_agent(llm, [search_tool], prompt)
agent_executor = AgentExecutor(agent=agent, tools=[search_tool], verbose=True)


def research_node(state: AgentState):
    result = agent_executor.invoke({"task": state["task"]})
    return {"search_results": [result["output"]]}


def report_node(state: AgentState):
    context = "\n".join(state["search_results"])
    response = llm.invoke(f"Escreva um relatório conciso baseado em:\n\n{context}")
    return {"report": response.content}


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("research", research_node)
    graph.add_node("report", report_node)
    graph.set_entry_point("research")
    graph.add_edge("research", "report")
    graph.add_edge("report", END)
    return graph.compile()


if __name__ == "__main__":
    app = build_graph()
    result = app.invoke({"task": "Quais são as tendências de IA Agentiva em 2025?"})
    print("\n### Relatório Final (Local) ###")
    print(result["report"])
