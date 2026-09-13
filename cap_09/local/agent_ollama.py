"""
cap_09 — Alternativa 100% Local: Finance Bot com Observabilidade via Ollama
Mesma arquitetura de projeto/agent.py, trocando o LLM de OpenRouter por
Ollama local. O Langfuse continua funcionando normalmente — self-hospede
com Docker e aponte LANGFUSE_HOST para sua instância local
(docker compose up -d no docker-compose.yml oficial do Langfuse).

Modelo: qwen3.5:7b
"""
import os

from langchain_community.tools import DuckDuckGoSearchRun
from langfuse.callback import CallbackHandler
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing import Annotated
from typing_extensions import TypedDict
import yfinance as yf

llm = ChatOllama(model="qwen3.5:7b", base_url="http://localhost:11434", temperature=0)


@tool
def get_stock_price(symbol: str) -> str:
    """Retorna o preço atual de uma ação dado seu símbolo (ticker)."""
    try:
        hist = yf.Ticker(symbol).history(period="1d")
        if hist.empty:
            return f"Não foi possível encontrar dados para o símbolo: {symbol}"
        return f"O preço atual da ação {symbol} é ${hist['Close'].iloc[-1]:.2f}."
    except Exception as e:
        return f"Erro ao buscar o preço da ação: {e}"


@tool
def search_financial_news(query: str) -> str:
    """Pesquisa por notícias financeiras recentes sobre um determinado tópico."""
    try:
        return DuckDuckGoSearchRun().run(f"financial news about {query}")
    except Exception as e:
        return f"Busca indisponível no momento ({e})."


tools = [get_stock_price, search_financial_news]
llm_with_tools = llm.bind_tools(tools)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def agent_node(state: State) -> dict:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")
app = graph.compile()


def build_langfuse_handler() -> CallbackHandler:
    return CallbackHandler(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY", "pk-lf-local"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY", "sk-lf-local"),
        host=os.getenv("LANGFUSE_HOST", "http://localhost:3000"),
    )


def run_agent(query: str, config: dict | None = None) -> str:
    state = app.invoke({"messages": [HumanMessage(content=query)]}, config=config)
    return state["messages"][-1].content


if __name__ == "__main__":
    handler = build_langfuse_handler()
    print(run_agent("Qual é o preço atual das ações da NVIDIA (NVDA)?", config={"callbacks": [handler]}))
    handler.flush()
