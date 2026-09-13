"""
cap_09 — Resiliência de Chamadas LLM: Retry + Fallback + Circuit Breaker
Módulo 10, Seção 5.7

Referência cruzada: Exercício 3 do cap_01 pode usar estes padrões
para lidar com erros HTTP 429 (rate limit) do OpenRouter.
"""
import os
import time
import logging
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_openai import ChatOpenAI

load_dotenv()
logger = logging.getLogger(__name__)


# --- Estratégia 1: Retry com backoff exponencial e jitter ---
def make_llm_primary():
    return ChatOpenAI(
        model="nvidia/llama-3.1-nemotron-70b-instruct:free",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
    )


def make_llm_fallback():
    """Provider alternativo quando o primário está indisponível."""
    return ChatOpenAI(
        model="meta-llama/llama-3.1-8b-instruct:free",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda rs: logger.warning(f"Retry {rs.attempt_number}/3 em {rs.next_action.sleep:.1f}s"),
)
def call_with_retry(llm, prompt: str) -> str:
    """Chamada com retry automático e backoff exponencial."""
    return llm.invoke(prompt).content


# --- Estratégia 2: Fallback de provider ---
def call_with_fallback(prompt: str) -> str:
    """Tenta o provider primário; se falhar, usa o fallback."""
    try:
        return call_with_retry(make_llm_primary(), prompt)
    except Exception as e:
        logger.error(f"Provider primário falhou: {e}. Usando fallback.")
        return call_with_retry(make_llm_fallback(), prompt)


# --- Circuit Breaker simples ---
class CircuitBreaker:
    """Evita chamadas repetidas a um provider com falhas consecutivas."""

    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._failures = 0
        self._last_failure_time: float | None = None
        self._open = False

    def call(self, fn, *args, **kwargs):
        if self._open:
            if time.time() - self._last_failure_time > self.recovery_timeout:
                self._open = False
                self._failures = 0
                logger.info("Circuit breaker: tentando recuperação.")
            else:
                raise RuntimeError("Circuit breaker ABERTO — provider indisponível.")
        try:
            result = fn(*args, **kwargs)
            self._failures = 0
            return result
        except Exception as e:
            self._failures += 1
            self._last_failure_time = time.time()
            if self._failures >= self.failure_threshold:
                self._open = True
                logger.error(f"Circuit breaker ABERTO após {self._failures} falhas.")
            raise


if __name__ == "__main__":
    prompt = "Explique o conceito de circuit breaker em uma linha."
    try:
        response = call_with_fallback(prompt)
        print(f"Resposta: {response}")
    except Exception as e:
        print(f"Todos os providers falharam: {e}")
