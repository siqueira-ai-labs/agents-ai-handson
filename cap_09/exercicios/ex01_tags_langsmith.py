"""
cap_09 — Exercício 1: Adicionando Tags no LangSmith
Dificuldade: Fácil | Tempo estimado: ~20 min

TAREFA:
Configure o agente do projeto para enviar tags e metadados para o LangSmith,
permitindo filtrar e analisar traces por categoria.

Requisitos:
1. Adicione as tags: ["cap_09", "finance-agent", "production"] ao run.
2. Adicione metadados: {"user_id": "test-user", "session_id": "abc123"}.
3. Configure o project name do LangSmith como "agents-ai-handson-cap09".
4. Verifique no dashboard do LangSmith que os traces aparecem com as tags.

DICA: Use RunnableConfig com tags= e metadata= no invoke().
"""
import os
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig

load_dotenv()

config = RunnableConfig(
    tags=["cap_09", "finance-agent", "production"],
    metadata={"user_id": "test-user", "session_id": "abc123"},
    run_name="finance-agent-cap09",
)

# TODO: importe o agente de cap_09/projeto/agent.py e invoque com o config acima


if __name__ == "__main__":
    print("Verificar traces em app.langsmith.com → project: agents-ai-handson-cap09")
    # TODO: execute o agente com o config e verifique as tags no dashboard
