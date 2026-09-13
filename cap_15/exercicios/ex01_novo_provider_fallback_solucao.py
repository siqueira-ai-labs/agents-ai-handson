"""
cap_15 — Solução Exercício 1: Adicionando um Novo Provedor de Fallback
Dificuldade: Fácil | Tempo estimado: ~20 min
"""
import logging
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def make_primary_llm() -> ChatOpenAI:
    """Provider primário — configurável via OPENROUTER_MODEL, padrão do livro."""
    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
    )


def make_fallback_llm() -> ChatOpenAI:
    """Provider de fallback — modelo diferente no OpenRouter, para sobreviver a
    rate limit ou descontinuação do modelo primário (não do provider inteiro)."""
    return ChatOpenAI(
        model=os.getenv("OPENROUTER_FALLBACK_MODEL", "meta-llama/llama-3.1-8b-instruct:free"),
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
    )


def health_check() -> dict[str, bool]:
    """Testa os dois providers na inicialização com uma chamada mínima."""
    status = {}
    for provider, make_llm in [("primary", make_primary_llm), ("fallback", make_fallback_llm)]:
        try:
            make_llm().invoke("ping")
            status[provider] = True
        except Exception as e:
            logger.warning(f"Health check falhou para {provider}: {e}")
            status[provider] = False
    return status


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
    print("Health check:", health_check())
    answer, provider = invoke_with_fallback("Qual o custo estimado de um Lambda AWS com 1M execuções/mês?")
    print(f"[{provider}] {answer}")
