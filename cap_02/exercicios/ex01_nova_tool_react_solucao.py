"""
cap_02 — Solução Exercício 1: Adicionando uma Nova Tool ao ReAct
Dificuldade: Fácil | Tempo estimado: ~20 min
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


@tool
def calculator(expression: str) -> str:
    """Avalia uma expressão matemática de forma segura."""
    from simpleeval import simple_eval
    try:
        return str(simple_eval(expression))
    except Exception as e:
        return f"Erro ao calcular '{expression}': {e}"


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)

tools = [TavilySearchResults(max_results=3), calculator]
llm_with_tools = llm.bind_tools(tools)


def agent_node(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


tool_node = ToolNode(tools)


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
    result = app.invoke({
        "messages": [("human", "Quanto é a raiz quadrada de 144 multiplicada por 7?")]
    })
    print("\n### Resposta Final ###")
    print(result["messages"][-1].content)
