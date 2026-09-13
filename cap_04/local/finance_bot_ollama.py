"""
cap_04 — Alternativa 100% Local: Finance Bot via Ollama
Modelo: qwen3.5:7b (excelente em dados estruturados e function calling)
"""
from typing import Annotated
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict
import yfinance as yf


@tool
def get_stock_price(ticker: str) -> str:
    """Retorna a cotação atual de uma ação."""
    try:
        price = yf.Ticker(ticker).fast_info.last_price
        return f"{ticker}: {price:.2f}" if price else "Cotação não encontrada"
    except Exception as e:
        return f"Erro: {str(e)}"


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatOllama(model="qwen3.5:7b", temperature=0, base_url="http://localhost:11434")
tools = [get_stock_price]
llm_with_tools = llm.bind_tools(tools)

graph = StateGraph(State)
graph.add_node("agent", lambda s: {"messages": [llm_with_tools.invoke(s["messages"])]})
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")
app = graph.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "local-1"}}
    result = app.invoke({"messages": [("human", "Qual é a cotação da AAPL?")]}, config=config)
    print(result["messages"][-1].content)
