"""
cap_01 — Solução do Exercício 3: Implementando o Ciclo PCA Manualmente
Dificuldade: Difícil | Tempo estimado: ~2-3h

Requer: pip install simpleeval
"""
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")


# --- Ferramentas ---

def calculator(expression: str) -> str:
    """Avalia uma expressão aritmética de forma segura com simpleeval."""
    from simpleeval import simple_eval
    try:
        return str(simple_eval(expression))
    except Exception as e:
        return f"Erro ao calcular '{expression}': {e}"


def get_current_datetime() -> str:
    """Retorna a data e hora atuais."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


TOOLS_MAP = {
    "calculator": calculator,
    "get_current_datetime": get_current_datetime,
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Avalia uma expressão matemática aritmética simples.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Expressão aritmética, ex: '1234 * 5678'",
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Retorna a data e hora atuais.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]


# --- API ---

def call_llm(messages: list) -> dict:
    """Percepção + Cognição: envia o histórico ao LLM e retorna a resposta."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/fgsiqueira/agent-ai-handson",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS_SCHEMA,
        "tool_choice": "auto",
    }
    response = requests.post(BASE_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()


# --- Loop PCA ---

def run_agent(user_input: str) -> str:
    """Loop Percepção → Cognição → Ação até finish_reason == 'stop'."""
    messages = [
        {"role": "system", "content": "Você é um assistente útil com acesso a ferramentas."},
        {"role": "user", "content": user_input},
    ]

    for iteration in range(10):
        print(f"\n  [Iteração {iteration + 1}] Chamando LLM...")

        # Percepção + Cognição
        response = call_llm(messages)
        choice = response["choices"][0]
        finish_reason = choice["finish_reason"]
        assistant_message = choice["message"]
        messages.append(assistant_message)

        print(f"  finish_reason: {finish_reason}")

        if finish_reason == "stop":
            return assistant_message.get("content", "")

        if finish_reason == "tool_calls":
            for tc in assistant_message.get("tool_calls", []):
                tool_name = tc["function"]["name"]
                raw_args = tc["function"].get("arguments", "{}")
                args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args

                print(f"  Executando: {tool_name}({args})")

                if tool_name not in TOOLS_MAP:
                    tool_result = f"Ferramenta '{tool_name}' não encontrada."
                else:
                    tool_result = TOOLS_MAP[tool_name](**args)

                print(f"  Resultado: {tool_result}")

                # Ação → resultado entra no histórico (próxima Percepção)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": str(tool_result),
                })
        else:
            return assistant_message.get("content", f"finish_reason inesperado: {finish_reason}")

    return "Número máximo de iterações atingido sem resposta final."


if __name__ == "__main__":
    print("Agente PCA Manual — sem frameworks")
    print("=" * 40)
    resposta = run_agent("Quanto é 1234 * 5678? E que horas são agora?")
    print(f"\nResposta final:\n{resposta}")
