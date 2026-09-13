"""
cap_01 — Exercício 1: Adicionando uma Nova Ferramenta
Dificuldade: Fácil | Tempo estimado: ~20 min

TAREFA:
No script do agente conversacional (baseado em abordagem1_langgraph.py),
adicione uma segunda ferramenta: uma função que retorna a data e hora atuais.

Requisitos:
1. Use o decorador @tool do LangChain para transformar a função em ferramenta.
2. Injete a nova ferramenta no AgentExecutor junto com a de busca.
3. Teste com a pergunta: "Que horas são agora e qual é a tendência de IA do momento?"

DICA: from langchain_core.tools import tool
"""
import os
from datetime import datetime
from dotenv import load_dotenv

# TODO: importe as dependências necessárias do LangChain

load_dotenv()


# TODO: defina a ferramenta get_current_datetime usando @tool
# Ela deve retornar a data e hora atuais formatadas como string.


# TODO: crie o agente incluindo tanto a ferramenta de busca quanto get_current_datetime


if __name__ == "__main__":
    # TODO: execute o agente com a pergunta abaixo
    question = "Que horas são agora e qual é a principal tendência de IA Agentiva?"
    print(f"Pergunta: {question}")
    # result = agent_executor.invoke({"input": question})
    # print(result["output"])
