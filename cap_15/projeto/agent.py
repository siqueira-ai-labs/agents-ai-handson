"""
cap_15 — Cloud Cost Analyst Agent
Bônus: Agentes na Nuvem (AWS, Azure, GCP)

Agente serverless que analisa custos de infraestrutura multi-cloud.
"""
import os
from typing import Annotated

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from tools import tool_list

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


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
