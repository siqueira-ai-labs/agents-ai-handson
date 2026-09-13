"""
cap_02 — Alternativa 100% Local: ReAct via Ollama
Modelo: mistral:7b (bom raciocínio em cadeia, 8 GB RAM)
         qwen3.5:7b para ex03 — saídas mais estruturadas
"""
from typing import Annotated
from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatOllama(model="mistral:7b", temperature=0, base_url="http://localhost:11434")
tools = [DuckDuckGoSearchRun()]
llm_with_tools = llm.bind_tools(tools)


def agent_node(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


tool_node = ToolNode(tools)

graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")
app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({"messages": [("human", "O que é o padrão ReAct em IA?")]})
    print(result["messages"][-1].content)
