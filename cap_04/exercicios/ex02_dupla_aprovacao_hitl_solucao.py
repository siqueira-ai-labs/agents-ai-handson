"""
cap_04 — Solução Exercício 2: Dupla Aprovação com HITL
Dificuldade: Médio | Tempo estimado: ~45 min
"""
import os
import sys
import pathlib
from typing import Annotated
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

load_dotenv()

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))
from finance_bot import get_stock_price, calculate_return  # noqa: E402

llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)


class State(TypedDict):
    messages: Annotated[list, add_messages]


tools = [get_stock_price, calculate_return]
llm_with_tools = llm.bind_tools(tools)


def agent_node(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


tool_node = ToolNode(tools)
checkpointer = MemorySaver()

graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")

app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["tools"],
    interrupt_after=["tools"],
)


def run_dupla_aprovacao(query: str, config: dict, approve_exec: bool = True, approve_result: bool = True):
    """Executa o fluxo de dupla aprovação de forma programática (útil para testes)."""
    state = app.invoke({"messages": [("human", query)]}, config=config)
    last = state["messages"][-1]

    if not (hasattr(last, "tool_calls") and last.tool_calls):
        return state["messages"][-1].content

    tool_name = last.tool_calls[0]["name"]

    if not approve_exec:
        return f"Operação cancelada antes da execução de '{tool_name}'."

    # Primeira aprovação: executa a ferramenta
    state = app.invoke(None, config=config)

    # Coletamos o resultado bruto da ferramenta
    tool_messages = [m for m in state["messages"] if isinstance(m, ToolMessage)]
    raw_result = tool_messages[-1].content if tool_messages else ""

    if not approve_result:
        return f"Resultado bruto (sem análise do agente): {raw_result}"

    # Segunda aprovação: agente continua a análise
    state = app.invoke(None, config=config)
    return state["messages"][-1].content


if __name__ == "__main__":
    print("Finance Bot — Dupla Aprovação HITL\n")
    config = {"configurable": {"thread_id": "dupla-aprovacao-1"}}

    while True:
        user_input = input("Você: ").strip()
        if user_input.lower() == "sair":
            break

        state = app.invoke({"messages": [("human", user_input)]}, config=config)
        last = state["messages"][-1]

        if not (hasattr(last, "tool_calls") and last.tool_calls):
            print(f"Bot: {last.content}")
            continue

        tool_name = last.tool_calls[0]["name"]
        print(f"\n⚠️  1ª Aprovação — Ferramenta: {tool_name}")
        if input("Executar? (s/n): ").strip().lower() != "s":
            print("Operação cancelada.")
            continue

        state = app.invoke(None, config=config)
        tool_messages = [m for m in state["messages"] if isinstance(m, ToolMessage)]
        raw = tool_messages[-1].content if tool_messages else ""
        print(f"\n📊 Resultado bruto: {raw}")

        print("\n⚠️  2ª Aprovação — Deseja que o agente continue a análise?")
        if input("Continuar? (s/n): ").strip().lower() != "s":
            print(f"Resultado: {raw}")
            continue

        state = app.invoke(None, config=config)
        print(f"\nBot: {state['messages'][-1].content}")
