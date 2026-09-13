"""
cap_10 — Integração com Langflow via API
Invoca um fluxo Langflow self-hosted por HTTP.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

LANGFLOW_BASE = os.getenv("LANGFLOW_BASE_URL", "http://localhost:7860")
FLOW_ID = os.getenv("LANGFLOW_FLOW_ID")  # UUID do fluxo exportado
API_KEY = os.getenv("LANGFLOW_API_KEY", "")


def run_flow(message: str, tweaks: dict | None = None, timeout: float = 60.0) -> dict:
    """Executa um fluxo Langflow via API REST."""
    url = f"{LANGFLOW_BASE}/api/v1/run/{FLOW_ID}"
    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": tweaks or {},
    }
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["x-api-key"] = API_KEY

    response = requests.post(url, json=payload, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    result = run_flow("Qual é a política de trocas e devoluções?")
    # A estrutura da resposta varia por versão do Langflow — inspecione result
    print(result)
