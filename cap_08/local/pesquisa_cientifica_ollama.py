"""
cap_08 — Alternativa 100% Local: Agente de Pesquisa Científica via Ollama
Mesma arquitetura de projeto/pesquisa_cientifica.py, trocando o
OpenAIChatCompletionClient (OpenRouter) por OllamaChatCompletionClient.

Modelo: qwen3.5:7b (bom em tool calling)
"""
import asyncio
import pathlib

from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_core.models import ModelFamily, ModelInfo
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_ext.models.ollama import OllamaChatCompletionClient

CODING_DIR = pathlib.Path(__file__).parent.parent / "coding"
CODING_DIR.mkdir(exist_ok=True)

MODEL_INFO = ModelInfo(
    vision=False,
    function_calling=True,
    json_output=False,
    family=ModelFamily.UNKNOWN,
    structured_output=False,
)


def build_model_client() -> OllamaChatCompletionClient:
    return OllamaChatCompletionClient(model="qwen3.5:7b", host="http://localhost:11434", model_info=MODEL_INFO)


def build_team(model_client: OllamaChatCompletionClient) -> SelectorGroupChat:
    researcher = AssistantAgent(
        name="Researcher",
        model_client=model_client,
        description="Especialista em encontrar informações e materiais brutos sobre o tópico pedido.",
        system_message=(
            "Você é um pesquisador especialista. Levante informações relevantes para o tópico "
            "solicitado, com base no seu conhecimento. Não escreva o relatório final."
        ),
    )
    reviewer = AssistantAgent(
        name="Reviewer",
        model_client=model_client,
        description="Sintetiza o material do Researcher em um relatório estruturado.",
        system_message=(
            "Você é um revisor de literatura científica. Sintetize o material do Researcher em "
            "um relatório coeso e entregue ao User_Proxy para aprovação."
        ),
    )
    code_executor = CodeExecutorAgent(
        name="CodeExecutor",
        code_executor=LocalCommandLineCodeExecutor(work_dir=str(CODING_DIR)),
        description="Executa blocos de código Python propostos e devolve o resultado.",
    )
    user_proxy = UserProxyAgent(
        name="User_Proxy",
        description=(
            "Representa o usuário: aprova o relatório final respondendo APPROVE seguido de "
            "TERMINATE. Só é chamado quando o Reviewer entregar um rascunho pronto."
        ),
    )

    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(16)
    return SelectorGroupChat(
        participants=[researcher, reviewer, code_executor, user_proxy],
        model_client=model_client,
        termination_condition=termination,
    )


async def run(task: str) -> None:
    model_client = build_model_client()
    try:
        team = build_team(model_client)
        await Console(team.run_stream(task=task))
    finally:
        await model_client.close()


if __name__ == "__main__":
    asyncio.run(run(
        "Encontre informações sobre RAG (Retrieval-Augmented Generation) em sistemas "
        "multiagente e escreva um relatório resumido. O relatório final deve ser aprovado "
        "pelo User_Proxy."
    ))
