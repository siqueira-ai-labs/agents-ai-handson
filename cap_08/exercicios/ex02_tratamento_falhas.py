"""
cap_08 — Exercício 2: Tratamento de Falhas com TerminatedException
Dificuldade: Médio | Tempo estimado: ~45 min

TAREFA:
Implemente tratamento robusto de falhas no fluxo AutoGen, incluindo
retry automático e log de erros quando a execução de código falha.

Requisitos:
1. Capture TerminatedException e outras exceções do AutoGen.
2. Implemente retry com máximo de 3 tentativas e backoff de 2s entre cada.
3. Se todas as tentativas falharem, retorne uma mensagem de erro amigável.
4. Registre cada tentativa em um arquivo de log cap_08/execution.log.
5. Teste com código que deliberadamente causa erro (ex: divisão por zero).
"""
import os
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename="cap_08/execution.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

MAX_RETRIES = 3
RETRY_DELAY = 2.0


async def run_with_retry(task: str, max_retries: int = MAX_RETRIES) -> str:
    """Executa o agente AutoGen com retry em caso de falha."""
    for attempt in range(1, max_retries + 1):
        try:
            logging.info(f"Tentativa {attempt}/{max_retries}: {task[:50]}")
            # TODO: invoque o agente AutoGen aqui
            raise NotImplementedError("Implemente a invocação do agente")
        except Exception as e:
            logging.error(f"Tentativa {attempt} falhou: {e}")
            if attempt < max_retries:
                await asyncio.sleep(RETRY_DELAY)
            else:
                return f"Falha após {max_retries} tentativas. Último erro: {e}"


if __name__ == "__main__":
    asyncio.run(run_with_retry("Calcule 1 / 0 e mostre o resultado."))
