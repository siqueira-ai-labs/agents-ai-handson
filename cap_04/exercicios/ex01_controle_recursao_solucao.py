"""
cap_04 — Solução Exercício 1: Controle de Recursão
Dificuldade: Fácil | Tempo estimado: ~20 min
"""
import os
import sys
import pathlib
from dotenv import load_dotenv
from langgraph.errors import GraphRecursionError

load_dotenv()

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))
from finance_bot import app  # noqa: E402


def run_with_recursion_limit(query: str, thread_id: str = "sessao-recursao", limit: int = 5):
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": limit,
    }
    try:
        state = app.invoke({"messages": [("human", query)]}, config=config)
        last = state["messages"][-1]
        if hasattr(last, "tool_calls") and last.tool_calls:
            print(f"⚠️  Aprovação necessária: {last.tool_calls[0]['name']}")
            state = app.invoke(None, config=config)
        return state["messages"][-1].content
    except GraphRecursionError:
        return "Limite de iterações atingido. Tente uma pergunta mais simples."


if __name__ == "__main__":
    print("Teste 1 — query simples:")
    print(run_with_recursion_limit("Qual a cotação de PETR4.SA?"))

    print("\nTeste 2 — query que pode gerar muitas iterações:")
    print(run_with_recursion_limit(
        "Compare as cotações de PETR4.SA, VALE3.SA e ITUB4.SA, calcule o retorno "
        "entre o menor e o maior e me diga qual delas teve melhor desempenho nos últimos 30 dias.",
        thread_id="sessao-recursao-2",
        limit=5,
    ))
