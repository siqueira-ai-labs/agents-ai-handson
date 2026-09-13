"""
cap_10 — Solução Exercício 3: Orquestração com Fallback entre Ferramentas
Dificuldade: Difícil | Tempo estimado: ~2-3h
"""
import logging
import os
import pathlib
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))
from nocode_integration import run_flow  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent / "cap_01" / "projeto"))

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


def _run_langchain_fallback(message: str) -> str:
    from abordagem1_langgraph import build_graph  # import tardio: só quando o fallback é usado

    app = build_graph()
    result = app.invoke({"task": message})
    return result["report"]


def run_with_fallback(message: str) -> tuple[str, str]:
    """Retorna (resposta, provider_usado)."""
    if is_langflow_healthy():
        try:
            result = run_flow(message, timeout=LANGFLOW_TIMEOUT)
            stats["langflow"] += 1
            texto = result.get("outputs", result)
            logger.info("Langflow respondeu com sucesso.")
            return str(texto), "langflow"
        except Exception as e:
            logger.warning(f"Langflow falhou: {e}. Usando fallback.")
    else:
        logger.warning("Langflow não está saudável (health check falhou). Usando fallback.")

    logger.info("Usando fallback LangChain.")
    stats["fallback"] += 1
    try:
        resposta = _run_langchain_fallback(message)
    except Exception as e:
        resposta = f"Fallback também falhou: {e}"
    return resposta, "langchain-fallback"


if __name__ == "__main__":
    queries = ["Qual a política de troca?", "Como rastrear meu pedido?", "Horário de atendimento?"]
    for q in queries:
        response, provider = run_with_fallback(q)
        print(f"[{provider}] {q[:40]} → {response[:60]}")

    total = stats["langflow"] + stats["fallback"]
    if total:
        print(f"\nEstatísticas: Langflow {stats['langflow']/total:.0%} | Fallback {stats['fallback']/total:.0%}")
