"""
cap_08 — Solução Exercício 1: Adicionando um Crítico ao Fibonacci
Dificuldade: Fácil | Tempo estimado: ~20 min
"""
import asyncio
import os
import pathlib

from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.models import ModelFamily, ModelInfo
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

CODING_DIR = pathlib.Path(__file__).parent.parent / "coding"
CODING_DIR.mkdir(exist_ok=True)

MODEL_INFO = ModelInfo(
    vision=False,
    function_calling=False,
    json_output=False,
    family=ModelFamily.UNKNOWN,
    structured_output=False,
)


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

    critic = AssistantAgent(
        name="critic",
        model_client=model_client,
        system_message=(
            "Você é um crítico de código. Avalie o código proposto quanto a corretude, "
            "eficiência e legibilidade antes de ele ser executado. Se houver problemas, "
            "aponte-os claramente; se estiver bom, diga apenas 'Aprovado para execução.'"
        ),
    )

    code_executor = CodeExecutorAgent(
        name="code_executor",
        code_executor=LocalCommandLineCodeExecutor(work_dir=str(CODING_DIR)),
    )

    return RoundRobinGroupChat(
        participants=[assistant, critic, code_executor],
        # 1 rodada completa: tarefa -> assistant -> critic -> code_executor
        termination_condition=MaxMessageTermination(4),
    )


async def run(task: str):
    model_client = build_model_client()
    try:
        team = build_team(model_client)
        return await team.run(task=task)
    finally:
        await model_client.close()


if __name__ == "__main__":
    resultado = asyncio.run(
        run("Escreva uma função Fibonacci com memoização e teste com n=40.")
    )
    for msg in resultado.messages:
        print(f"[{msg.source}] {msg.content}")
