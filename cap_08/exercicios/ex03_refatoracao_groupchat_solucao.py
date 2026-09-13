"""
cap_08 — Solução Exercício 3: Pipeline de Refatoração com GroupChat
Dificuldade: Difícil | Tempo estimado: ~2-3h
"""
import asyncio
import os
import pathlib

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_core.models import ModelFamily, ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

CODE_TO_REFACTOR = """
def calc(x,y,z):
    r=0
    for i in range(x):
        r=r+y
    r=r*z
    return r
"""

OUTPUT_DIR = pathlib.Path(__file__).parent.parent / "outputs"
OUTPUT_PATH = OUTPUT_DIR / "refactored.py"

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


def build_team(model_client: OpenAIChatCompletionClient) -> SelectorGroupChat:
    analyzer = AssistantAgent(
        name="Analyzer",
        model_client=model_client,
        description="Identifica code smells e problemas de qualidade no código.",
        system_message=(
            "Você analisa código Python e lista objetivamente os code smells e "
            "problemas de qualidade encontrados (nomes ruins, falta de tipagem, "
            "complexidade desnecessária, etc). Não reescreva o código, apenas liste os problemas."
        ),
    )
    refactorer = AssistantAgent(
        name="Refactorer",
        model_client=model_client,
        description="Aplica as sugestões do Analyzer e produz código refatorado.",
        system_message=(
            "Você reescreve o código aplicando as sugestões do Analyzer, sempre entregando "
            "a versão refatorada completa em um único bloco markdown (```python ... ```)."
        ),
    )
    tester = AssistantAgent(
        name="Tester",
        model_client=model_client,
        description="Escreve testes unitários para o código refatorado.",
        system_message=(
            "Você escreve testes unitários com pytest para o código refatorado mais recente, "
            "em um bloco markdown (```python ... ```)."
        ),
    )
    reviewer = AssistantAgent(
        name="Reviewer",
        model_client=model_client,
        description="Aprovação final do código refatorado e dos testes.",
        system_message=(
            "Você avalia se o código refatorado e os testes do Tester estão satisfatórios. "
            "Se ainda faltar algo, peça ajustes especificamente ao Refactorer ou ao Tester. "
            "Quando estiver satisfeito, responda exatamente 'APPROVED' e nada mais."
        ),
    )

    return SelectorGroupChat(
        participants=[analyzer, refactorer, tester, reviewer],
        model_client=model_client,
        termination_condition=TextMentionTermination("APPROVED"),
        max_turns=6,
    )


def extract_last_code_block(messages, source: str) -> str | None:
    """Retorna o conteúdo do último bloco ```python ...``` emitido pelo agente `source`."""
    for msg in reversed(messages):
        if getattr(msg, "source", None) != source:
            continue
        content = msg.content if isinstance(msg.content, str) else ""
        if "```" not in content:
            continue
        parts = content.split("```")
        # parts alterna texto/código; blocos de código ficam nos índices ímpares
        for block in reversed(parts[1::2]):
            code = block.split("\n", 1)[1] if block.startswith("python") else block
            if code.strip():
                return code.strip() + "\n"
    return None


async def run(task: str) -> str | None:
    """Executa o pipeline e salva o código refatorado final em disco. Retorna o path salvo."""
    model_client = build_model_client()
    try:
        team = build_team(model_client)
        result = await team.run(task=task)
        code = extract_last_code_block(result.messages, source="Refactorer")
        if code:
            OUTPUT_DIR.mkdir(exist_ok=True)
            OUTPUT_PATH.write_text(code)
            return str(OUTPUT_PATH)
        return None
    finally:
        await model_client.close()


if __name__ == "__main__":
    tarefa = f"""
    Refatore o código Python abaixo, escreva testes unitários para ele e só aprove
    quando refatoração e testes estiverem satisfatórios:

    ```python
    {CODE_TO_REFACTOR}
    ```
    """
    caminho = asyncio.run(run(tarefa))
    print(f"Código refatorado salvo em: {caminho}" if caminho else "Nenhum código refatorado foi produzido.")
