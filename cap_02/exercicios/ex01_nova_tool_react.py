"""
cap_02 — Exercício 1: Adicionando uma Nova Tool ao ReAct
Dificuldade: Fácil | Tempo estimado: ~20 min

TAREFA:
Adicione uma ferramenta de calculadora ao agente ReAct de cap_02/projeto/react_assistant.py.
A ferramenta deve receber uma expressão matemática como string e retornar o resultado.

Requisitos:
1. Use o decorador @tool para criar a ferramenta `calculator`.
2. Use `simpleeval` para avaliação segura da expressão (pip install simpleeval).
3. Inclua a ferramenta na lista `tools` do agente.
4. Teste com: "Quanto é a raiz quadrada de 144 multiplicada por 7?"
"""
import os
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()


# TODO: implemente o @tool calculator usando simpleeval para avaliação segura
# from simpleeval import simple_eval
# Uso: simple_eval("2 + 2 * 10")  → retorna 22 (sem executar código arbitrário)


# TODO: adicione calculator à lista de tools do agente ReAct de react_assistant.py


if __name__ == "__main__":
    # TODO: teste o agente com a pergunta matemática
    pass
