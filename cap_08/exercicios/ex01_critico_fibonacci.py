"""
cap_08 — Exercício 1: Adicionando um Crítico ao Fibonacci
Dificuldade: Fácil | Tempo estimado: ~20 min

TAREFA:
Adicione um agente "Crítico" ao fluxo do agente de Fibonacci. O crítico deve
revisar o código gerado antes de ser executado e sugerir otimizações.

Requisitos:
1. Crie um AssistantAgent chamado "critic" com system_message focado em revisão.
2. Use RoundRobinGroupChat para orquestrar: assistant → critic → user_proxy.
3. O crítico deve avaliar: corretude, eficiência e legibilidade.
4. Teste com a tarefa: "Escreva uma função Fibonacci com memoização e teste com n=40."
"""
import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_core.models import ModelFamily, ModelInfo
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

client = OpenAIChatCompletionClient(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free"),
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    # Modelos servidos via OpenRouter não são reconhecidos automaticamente
    # pelo cliente OpenAI-compatible do AutoGen — é preciso declarar model_info.
    model_info=ModelInfo(
        vision=False,
        function_calling=False,
        json_output=False,
        family=ModelFamily.UNKNOWN,
        structured_output=False,
    ),
)

# TODO: crie os agentes assistant, critic e user_proxy
# TODO: configure RoundRobinGroupChat
# TODO: execute com a tarefa de Fibonacci


if __name__ == "__main__":
    import asyncio

    async def main():
        # TODO: implemente o fluxo
        pass

    asyncio.run(main())
