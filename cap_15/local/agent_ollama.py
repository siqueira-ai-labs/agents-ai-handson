"""
cap_15 — Alternativa 100% Local: Cloud Cost Analyst via Ollama
Mesma arquitetura de projeto/agent.py, trocando o LLM de OpenRouter por
Ollama local. As tools de custo continuam chamando as APIs reais de
AWS/Azure/GCP (não têm equivalente "local") — só o raciocínio do agente
roda localmente.

Modelo: qwen3.5:7b
"""
import pathlib
import sys
from typing import Annotated

from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))
from tools import tool_list  # noqa: E402


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatOllama(model="qwen3.5:7b", base_url="http://localhost:11434", temperature=0)
llm_with_tools = llm.bind_tools(tool_list)

graph = StateGraph(State)
graph.add_node("agent", lambda s: {"messages": [llm_with_tools.invoke(s["messages"])]})
graph.add_node("tools", ToolNode(tool_list))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")
app = graph.compile()


def run_agent(query: str) -> str:
    result = app.invoke({"messages": [("human", query)]})
    return result["messages"][-1].content


if __name__ == "__main__":
    print(run_agent("Qual o custo estimado do meu uso de EC2 nos últimos 30 dias?"))
