"""
cap_08 — Solução Exercício 2: Tratamento de Falhas com TerminatedException
Dificuldade: Médio | Tempo estimado: ~45 min
"""
import asyncio
import logging
import os
import pathlib

from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.base import TerminatedException
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.models import ModelFamily, ModelInfo
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

CODING_DIR = pathlib.Path(__file__).parent.parent / "coding"
CODING_DIR.mkdir(exist_ok=True)
LOG_PATH = pathlib.Path(__file__).parent.parent / "execution.log"

# Logger dedicado (não usa logging.basicConfig) para não capturar os logs
# internos, bem verbosos, do runtime do AutoGen na raiz do logging.
logger = logging.getLogger("cap08.tratamento_falhas")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.FileHandler(str(LOG_PATH))
    _handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_handler)

MAX_RETRIES = 3
RETRY_DELAY = 2.0

MODEL_INFO = ModelInfo(
    vision=False,
    function_calling=False,
    json_output=False,
    family=ModelFamily.UNKNOWN,
    structured_output=False,
)

CODE_EXECUTION_ERROR_MARKER = "exited with an error"


def build_model_client() -> OpenAIChatCompletionClient:
    return OpenAIChatCompletionClient(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        model_info=MODEL_INFO,
    )


def build_team(model_client: OpenAIChatCompletionClient) -> RoundRobinGroupChat:
    assistant = AssistantAgent(
        name="assistant",
        model_client=model_client,
        system_message=(
            "Você escreve código Python para resolver a tarefa pedida, sempre em um "
            "único bloco markdown (```python ... ```)."
        ),
    )
    code_executor = CodeExecutorAgent(
        name="code_executor",
        code_executor=LocalCommandLineCodeExecutor(work_dir=str(CODING_DIR)),
    )
    return RoundRobinGroupChat(
        participants=[assistant, code_executor],
        # 1 rodada por tentativa: tarefa -> assistant -> code_executor
        termination_condition=MaxMessageTermination(3),
    )


async def run_with_retry(
    task: str,
    model_client: OpenAIChatCompletionClient | None = None,
    max_retries: int = MAX_RETRIES,
) -> str:
    """Executa o agente AutoGen com retry em caso de falha na execução de código."""
    client = model_client or build_model_client()
    try:
        for attempt in range(1, max_retries + 1):
            logger.info(f"Tentativa {attempt}/{max_retries}: {task[:50]}")
            try:
                # Cada tentativa usa um time novo: um time já terminado levanta
                # TerminatedException se for reutilizado sem reset().
                team = build_team(client)
                result = await team.run(task=task)

                execution_messages = [m for m in result.messages if m.source == "code_executor"]
                if execution_messages and CODE_EXECUTION_ERROR_MARKER in execution_messages[-1].content:
                    raise RuntimeError(execution_messages[-1].content)

                logger.info(f"Tentativa {attempt} bem-sucedida.")
                return execution_messages[-1].content if execution_messages else result.messages[-1].content
            except (TerminatedException, RuntimeError) as e:
                logger.error(f"Tentativa {attempt} falhou: {e}")
                if attempt < max_retries:
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    return f"Falha após {max_retries} tentativas. Último erro: {e}"
    finally:
        if model_client is None:
            await client.close()


if __name__ == "__main__":
    print(asyncio.run(run_with_retry("Calcule 1 / 0 e mostre o resultado.")))
