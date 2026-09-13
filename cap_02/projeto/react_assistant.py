"""
cap_02 — Assistente de Pesquisa com Padrão ReAct + LangGraph
Módulo 3: Arquiteturas e Padrões de Design

O padrão ReAct intercala Raciocínio (Thought) e Ação (Action) em um loop:
Thought → Action → Observation → Thought → ... → Final Answer
"""
import os
from typing import Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

load_dotenv()

# --- Estado ---
class State(TypedDict):
    messages: Annotated[list, add_messages]


# --- LLM e ferramentas ---
llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)

tools = [TavilySearchResults(max_results=3)]
llm_with_tools = llm.bind_tools(tools)


# --- Nós ---
def agent_node(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


tool_node = ToolNode(tools)


# --- Grafo ReAct ---
def build_react_graph():
    graph = StateGraph(State)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    return graph.compile()


if __name__ == "__main__":
    app = build_react_graph()
    result = app.invoke({"messages": [("human", "Pesquise sobre o estado atual do LangGraph em 2025.")]})
    print("\n### Resposta Final ###")
    print(result["messages"][-1].content)
