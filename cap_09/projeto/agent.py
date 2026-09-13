"""
cap_09 — Finance Bot com Observabilidade (Langfuse + LangSmith)
Módulo 10: Observabilidade de Agentes

LangSmith traça automaticamente via variáveis de ambiente
(LANGCHAIN_TRACING_V2/LANGCHAIN_API_KEY/LANGCHAIN_PROJECT) — nenhuma
instrumentação de código é necessária. O Langfuse é adicionado via
CallbackHandler, passado explicitamente no config de cada invocação.
"""
import os
from typing import Annotated

import yfinance as yf
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langfuse.callback import CallbackHandler
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)


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
        return f"Busca indisponível no momento ({e}). Baseie-se no seu conhecimento geral."


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
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
    )


def run_agent(query: str, config: dict | None = None) -> str:
    """Executa o agente. Passe config={"callbacks": [langfuse_handler], "tags": [...]}
    para instrumentar com Langfuse e/ou tags do LangSmith."""
    state = app.invoke({"messages": [HumanMessage(content=query)]}, config=config)
    return state["messages"][-1].content


if __name__ == "__main__":
    langfuse_handler = build_langfuse_handler()
    run_config = {"callbacks": [langfuse_handler]}

    print(run_agent("Qual é o preço atual das ações da NVIDIA (NVDA)?", config=run_config))
    print(run_agent(
        "Pesquise notícias recentes sobre a Apple e depois me diga o preço de suas ações (AAPL).",
        config=run_config,
    ))

    langfuse_handler.flush()
