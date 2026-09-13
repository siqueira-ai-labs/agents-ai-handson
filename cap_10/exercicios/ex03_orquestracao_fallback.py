"""
cap_10 — Exercício 3: Orquestração com Fallback entre Ferramentas
Dificuldade: Difícil | Tempo estimado: ~2-3h

TAREFA:
Implemente um orquestrador Python que tenta executar o fluxo Langflow e, se
falhar (timeout ou erro), faz fallback para um agente LangChain local.

Requisitos:
1. Tente o fluxo Langflow com timeout de 10s.
2. Se falhar, use o agente LangChain (cap_01/projeto/abordagem1_langgraph.py) como fallback.
3. Registre qual provider foi usado em cada chamada.
4. Implemente health check para o Langflow antes de tentar.
5. Exiba métricas ao final: % de chamadas via Langflow vs fallback.
"""
import os
import time
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LANGFLOW_BASE = os.getenv("LANGFLOW_BASE_URL", "http://localhost:7860")
LANGFLOW_TIMEOUT = 10.0

stats = {"langflow": 0, "fallback": 0}


def is_langflow_healthy() -> bool:
    """Verifica se o Langflow está acessível."""
    try:
        r = requests.get(f"{LANGFLOW_BASE}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def run_with_fallback(message: str) -> tuple[str, str]:
    """Retorna (resposta, provider_usado)."""
    if is_langflow_healthy():
        try:
            # TODO: invoque o fluxo Langflow com timeout
            pass
        except Exception as e:
            logger.warning(f"Langflow falhou: {e}. Usando fallback.")

    # Fallback LangChain
    logger.info("Usando fallback LangChain.")
    stats["fallback"] += 1
    # TODO: invoque cap_01/projeto/abordagem1_langgraph.py
    return "resposta_fallback_placeholder", "langchain-fallback"


if __name__ == "__main__":
    queries = ["Qual a política de troca?", "Como rastrear meu pedido?", "Horário de atendimento?"]
    for q in queries:
        response, provider = run_with_fallback(q)
        print(f"[{provider}] {q[:40]} → {response[:60]}")

    total = stats["langflow"] + stats["fallback"]
    if total:
        print(f"\nEstatísticas: Langflow {stats['langflow']/total:.0%} | Fallback {stats['fallback']/total:.0%}")
