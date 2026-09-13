"""
cap_04 — Finance Bot com Memória e HITL
Módulo 5: Construindo Agentes com LangGraph

Funcionalidades:
- Memória de curto prazo via MemorySaver (checkpoints)
- Human-in-the-Loop (HITL) para aprovação de operações críticas
- Ferramentas: cotação de ações, cálculo de retorno
"""
import os
from typing import Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict
import yfinance as yf

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)


# --- Ferramentas financeiras ---
@tool
def get_stock_price(ticker: str) -> str:
    """Retorna a cotação atual de uma ação pelo ticker (ex: AAPL, PETR4.SA)."""
    try:
        stock = yf.Ticker(ticker)
        price = stock.fast_info.last_price
        return f"{ticker}: R$ {price:.2f}" if price else f"Cotação não encontrada para {ticker}"
    except Exception as e:
        return f"Erro ao buscar {ticker}: {str(e)}"


@tool
def calculate_return(initial: float, final: float) -> str:
    """Calcula o retorno percentual entre dois valores."""
    if initial <= 0:
        return "Valor inicial deve ser maior que zero."
    return f"Retorno: {((final - initial) / initial) * 100:.2f}%"


# --- Estado ---
class State(TypedDict):
    messages: Annotated[list, add_messages]


# --- Grafo com HITL ---
tools = [get_stock_price, calculate_return]
llm_with_tools = llm.bind_tools(tools)


def agent_node(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


tool_node = ToolNode(tools)

# Interrupção antes de executar ferramentas (HITL)
checkpointer = MemorySaver()

graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")

app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["tools"],  # pausa para aprovação humana
)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "sessao-1"}}
    print("Finance Bot — digite 'sair' para encerrar\n")

    while True:
        user_input = input("Você: ")
        if user_input.lower() == "sair":
            break

        state = app.invoke({"messages": [("human", user_input)]}, config=config)
        last = state["messages"][-1]

        if hasattr(last, "tool_calls") and last.tool_calls:
            print(f"\n⚠️  Aprovação necessária. Ferramenta: {last.tool_calls[0]['name']}")
            approve = input("Aprovar? (s/n): ").strip().lower()
            if approve == "s":
                state = app.invoke(None, config=config)
                print(f"\nBot: {state['messages'][-1].content}")
            else:
                print("Operação cancelada.")
        else:
            print(f"\nBot: {last.content}")
