"""
cap_04 — Exercício 1: Controle de Recursão
Dificuldade: Fácil | Tempo estimado: ~20 min

TAREFA:
Adicione um limite máximo de iterações ao Finance Bot para evitar loops infinitos.
O LangGraph tem suporte nativo a isso via `recursion_limit`.

Requisitos:
1. Configure recursion_limit=5 no invoke() do grafo.
2. Capture a exceção GraphRecursionError quando o limite for atingido.
3. Exiba uma mensagem amigável ao usuário em vez de um traceback.
4. Teste com uma query que normalmente geraria muitas chamadas de ferramenta.
"""
import os
from dotenv import load_dotenv
from langgraph.errors import GraphRecursionError

load_dotenv()

# TODO: importe e configure o Finance Bot de cap_04/projeto/finance_bot.py


if __name__ == "__main__":
    config = {
        "configurable": {"thread_id": "sessao-recursao"},
        # TODO: adicione recursion_limit=5
    }
    try:
        # TODO: invoque o agente com uma query complexa
        pass
    except GraphRecursionError:
        print("Limite de iterações atingido. Tente uma pergunta mais simples.")
