"""
cap_01 — Exercício 3: Implementando o Ciclo PCA Manualmente
Dificuldade: Difícil | Tempo estimado: ~2-3h

TAREFA:
Construa um agente simples do zero usando apenas a API do OpenRouter (compatível
com o protocolo OpenAI). SEM usar LangChain, LangGraph ou qualquer framework.

Requisitos:
1. Implemente o loop Percepção → Cognição → Ação manualmente.
2. Defina pelo menos 2 ferramentas como funções Python (ex: calculadora, data/hora).
3. Gerencie o array de mensagens (system, user, assistant, tool) manualmente.
4. Implemente detecção de tool_calls na resposta do LLM e execução da ferramenta.
5. O loop deve continuar até o LLM não chamar mais ferramentas (finish_reason=stop).

DICA: O maior desafio é formatar corretamente as mensagens de sistema, usuário e
ferramenta no array de histórico. Ver: openrouter.ai/docs para o formato da API.

Referência cruzada: Módulo 10 (seção 5.7) — rate limiting e retry com backoff.
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "nvidia/llama-3.1-nemotron-70b-instruct:free"


# --- Ferramentas ---
def calculator(expression: str) -> str:
    """Avalia uma expressão matemática simples.

    Use ast.literal_eval() apenas para literais, ou a biblioteca `simpleeval`
    para expressões aritméticas seguras. Nunca use eval() — executa código arbitrário.
    Sugestão: pip install simpleeval
    """
    # TODO: implemente com simpleeval.simple_eval(expression)
    raise NotImplementedError


def get_current_datetime() -> str:
    """Retorna a data e hora atuais."""
    # TODO: implemente
    raise NotImplementedError


TOOLS_MAP = {
    "calculator": calculator,
    "get_current_datetime": get_current_datetime,
}

# Definição de ferramentas no formato OpenAI function calling
TOOLS_SCHEMA = [
    # TODO: defina o schema JSON de cada ferramenta
]


def call_llm(messages: list) -> dict:
    """Faz a chamada à API do OpenRouter."""
    # TODO: implemente a chamada HTTP com requests
    # Inclua os headers necessários (Authorization, HTTP-Referer)
    raise NotImplementedError


def run_agent(user_input: str):
    """Loop principal do agente: Percepção → Cognição → Ação."""
    messages = [
        {"role": "system", "content": "Você é um assistente útil com acesso a ferramentas."},
        {"role": "user", "content": user_input},
    ]

    # TODO: implemente o loop:
    # 1. Chame call_llm(messages)
    # 2. Se finish_reason == "tool_calls": execute a ferramenta e adicione o resultado
    # 3. Se finish_reason == "stop": retorne a resposta final
    # 4. Limite o loop a 10 iterações para evitar loops infinitos


if __name__ == "__main__":
    print("Agente PCA Manual — sem frameworks")
    print("=" * 40)
    resposta = run_agent("Quanto é 1234 * 5678? E que horas são agora?")
    print(f"\nResposta final: {resposta}")
