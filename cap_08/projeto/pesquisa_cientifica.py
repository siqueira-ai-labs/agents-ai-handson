"""
cap_08 — Agente de Pesquisa Científica com AutoGen v0.4
Módulo 9: Desenvolvimento Avançado com Autogen

Time de especialistas colaborando via SelectorGroupChat:
- Researcher: levanta informações e materiais brutos sobre o tópico
- Reviewer: sintetiza os achados em um relatório estruturado
- Programmer: escreve código quando é preciso processar ou analisar dados
- CodeExecutor: executa os blocos de código propostos pelo Programmer
- User_Proxy: aprova o relatório final (human-in-the-loop)
"""
import asyncio
import os
import pathlib

from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent, UserProxyAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_core.models import ModelFamily, ModelInfo
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv()

CODING_DIR = pathlib.Path(__file__).parent.parent / "coding"
CODING_DIR.mkdir(exist_ok=True)

# Modelos servidos via OpenRouter não são reconhecidos automaticamente pelo
# cliente OpenAI-compatible do AutoGen — é preciso declarar model_info manualmente.
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
    researcher = AssistantAgent(
        name="Researcher",
        model_client=model_client,
        description="Especialista em encontrar informações e materiais brutos sobre o tópico pedido.",
        system_message="""
        Você é um pesquisador especialista. Sua função é levantar informações e dados
        relevantes para o tópico solicitado, com base no seu conhecimento.
        Você não escreve o relatório final — apenas fornece os materiais brutos para o Reviewer.
        Não responda TERMINATE; passe a vez para o Reviewer quando terminar de levantar o material.
        """,
    )

    reviewer = AssistantAgent(
        name="Reviewer",
        model_client=model_client,
        description="Sintetiza o material do Researcher em um relatório estruturado.",
        system_message="""
        Você é um revisor de literatura científica. Leia o material fornecido pelo Researcher,
        extraia os pontos-chave e sintetize um rascunho de relatório coeso e estruturado.
        Se algum dado precisar ser processado ou calculado, peça ao Programmer.
        Quando o rascunho estiver pronto, entregue-o ao User_Proxy para aprovação final.
        """,
    )

    programmer = AssistantAgent(
        name="Programmer",
        model_client=model_client,
        description="Escreve e propõe scripts Python para processar ou analisar dados, quando solicitado.",
        system_message="""
        Você é um programador Python experiente. Quando o Researcher ou o Reviewer precisarem
        processar dados, escreva um script Python objetivo em um bloco de código markdown
        (```python ... ```) para que o CodeExecutor rode e devolva o resultado.
        Não escreva código se ninguém pediu.
        """,
    )

    code_executor = CodeExecutorAgent(
        name="CodeExecutor",
        code_executor=LocalCommandLineCodeExecutor(work_dir=str(CODING_DIR)),
        description="Executa os blocos de código Python propostos pelo Programmer e devolve o resultado.",
    )

    user_proxy = UserProxyAgent(
        name="User_Proxy",
        description=(
            "Representa o usuário humano: aprova o relatório final do Reviewer e encerra a tarefa "
            "respondendo APPROVE seguido de TERMINATE. Só deve ser chamado quando o Reviewer "
            "entregar um rascunho de relatório pronto para aprovação."
        ),
    )

    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(16)

    return SelectorGroupChat(
        participants=[researcher, reviewer, programmer, code_executor, user_proxy],
        model_client=model_client,
        termination_condition=termination,
        selector_prompt=(
            "Você está coordenando um time de pesquisa científica com os papéis abaixo:\n"
            "{roles}\n\n"
            "Histórico da conversa até agora:\n{history}\n\n"
            "Escolha quem deve falar em seguida entre {participants}. "
            "Responda apenas com o nome do papel."
        ),
    )


async def run(task: str) -> None:
    model_client = build_model_client()
    team = build_team(model_client)
    try:
        await Console(team.run_stream(task=task))
    finally:
        await model_client.close()


if __name__ == "__main__":
    tarefa = """
    Encontre informações sobre o uso de 'Retrieval-Augmented Generation (RAG)'
    em sistemas de múltiplos agentes de IA. Quero um relatório que cubra:
    1. O que é RAG e como funciona.
    2. Quais são os benefícios de usar RAG com agentes de IA.
    3. Exemplos de aplicação ou estudos de caso.
    4. Quais são os desafios ou limitações.
    O Researcher deve levantar o material, o Reviewer escreve o relatório,
    e o Programmer pode ser chamado se for necessário processar dados.
    O relatório final deve ser aprovado pelo User_Proxy.
    """
    asyncio.run(run(tarefa))
