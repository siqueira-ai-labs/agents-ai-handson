"""
cap_15 — Exercício 1: Adicionando um Novo Provedor de Fallback
Dificuldade: Fácil | Tempo estimado: ~20 min

TAREFA:
Adicione OpenRouter como provedor de fallback de LLM para o agente cloud,
caso o provider configurado por padrão esteja indisponível.

Requisitos:
1. Configure dois LLMs: primário (provider padrão) e fallback (OpenRouter).
2. Implemente a lógica de fallback usando try/except.
3. Registre em log qual provider foi usado em cada invocação.
4. Adicione health check que testa os dois providers na inicialização.
"""
import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def make_primary_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model="nvidia/llama-3.1-nemotron-70b-instruct:free",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
    )


def make_fallback_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model="meta-llama/llama-3.1-8b-instruct:free",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
    )


def invoke_with_fallback(prompt: str) -> tuple[str, str]:
    """Invoca o LLM com fallback automático. Retorna (resposta, provider)."""
    for provider, make_llm in [("primary", make_primary_llm), ("fallback", make_fallback_llm)]:
        try:
            response = make_llm().invoke(prompt)
            logger.info(f"Provider usado: {provider}")
            return response.content, provider
        except Exception as e:
            logger.warning(f"Provider {provider} falhou: {e}")
    return "Nenhum provider disponível.", "none"


if __name__ == "__main__":
    answer, provider = invoke_with_fallback("Qual o custo estimado de um Lambda AWS com 1M execuções/mês?")
    print(f"[{provider}] {answer}")
