"""
cap_10 — Alternativa 100% Local: Fallback via Ollama
O Langflow em si roda local via Docker independentemente do provider de LLM
(troque o componente de LLM dentro do fluxo, pela UI, para apontar a um
modelo Ollama) — não há o que trocar em Python para isso. O que É possível
trocar aqui é o fallback do exercício 3 (projeto/nocode_integration.py):
em vez de cair para um agente LangChain via OpenRouter, cai para Ollama
local, então a demonstração inteira funciona sem nenhuma API paga.

Modelo: qwen3.5:7b
"""
import logging
import pathlib
import sys

from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))
from nocode_integration import run_flow  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

llm = ChatOllama(model="qwen3.5:7b", base_url="http://localhost:11434", temperature=0)


def run_with_local_fallback(message: str) -> tuple[str, str]:
    """Tenta o fluxo Langflow; se falhar, cai para Ollama local. Retorna (resposta, provider)."""
    try:
        resultado = run_flow(message, timeout=10.0)
        return str(resultado.get("outputs", resultado)), "langflow"
    except Exception as e:
        logger.warning(f"Langflow indisponível ({e}). Usando fallback local (Ollama).")

    resposta = llm.invoke([HumanMessage(content=message)])
    return resposta.content, "ollama-fallback"


if __name__ == "__main__":
    resposta, provider = run_with_local_fallback("Qual a política de troca de produtos?")
    print(f"[{provider}] {resposta}")
