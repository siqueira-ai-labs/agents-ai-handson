"""
cap_12 — Solução Exercício 3: Moderação de Saída com Llama Guard 3
Dificuldade: Difícil | Tempo estimado: ~2-3h

Requer Ollama rodando localmente com o modelo Llama Guard 3 disponível:
    ollama pull llama-guard3
"""
import hashlib
import logging
import os
import pathlib

import requests
from dotenv import load_dotenv

load_dotenv()

LOG_PATH = pathlib.Path(__file__).parent.parent / "moderation.log"
logger = logging.getLogger("cap12.moderation")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.FileHandler(str(LOG_PATH))
    _handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_handler)

SAFE_FALLBACK = "Não posso fornecer essa informação. Por favor, consulte um profissional."

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLAMA_GUARD_MODEL = os.getenv("LLAMA_GUARD_MODEL", "llama-guard3")


def hash_content(text: str) -> str:
    """Gera hash SHA-256 do conteúdo para log sem armazenar o dado original."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def _parse_llama_guard_response(text: str) -> tuple[bool, str | None]:
    """Interpreta a resposta do Llama Guard: 'safe' ou 'unsafe\\n<categorias>'."""
    text = text.strip().lower()
    if text.startswith("safe"):
        return True, None
    if text.startswith("unsafe"):
        categoria = text.split("\n", 1)[1].strip() if "\n" in text else ""
        return False, categoria or "unspecified"
    logger.warning(f"Resposta inesperada do Llama Guard: {text[:80]!r}")
    return True, None  # fail-open: não derruba a resposta por erro de parsing


def moderate_output(agent_response: str) -> tuple[str, bool]:
    """
    Modera a saída do agente com Llama Guard via Ollama.
    Retorna (resposta_final, foi_bloqueada).
    """
    prompt = (
        "Task: Check if there is unsafe content in the 'Agent' messages in conversations "
        "according to our safety policy.\n\n"
        f"Agent: {agent_response}\n\n"
        "Provide your safety assessment. First line must read 'safe' or 'unsafe'. "
        "If unsafe, a second line must include a comma-separated list of violated categories."
    )
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": LLAMA_GUARD_MODEL, "prompt": prompt, "stream": False},
            timeout=30,
        )
        resp.raise_for_status()
        texto = resp.json().get("response", "")
    except Exception as e:
        logger.error(f"Llama Guard indisponível ({e}); liberando resposta sem moderação (fail-open).")
        return agent_response, False

    safe, categoria = _parse_llama_guard_response(texto)
    logger.info(f"input_hash={hash_content(agent_response)} classification={'safe' if safe else 'unsafe'} categoria={categoria}")

    if not safe:
        return SAFE_FALLBACK, True
    return agent_response, False


def create_moderation_middleware(app, agent_fn):
    """Envolve a rota /chat do Flask com moderação de saída via Llama Guard."""
    from flask import jsonify, request

    @app.route("/chat/moderated", methods=["POST"])
    def chat_moderated():
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Campo 'message' é obrigatório"}), 400

        resposta_bruta = agent_fn(data["message"])
        resposta_final, bloqueada = moderate_output(resposta_bruta)
        return jsonify({"response": resposta_final, "moderated": bloqueada})

    return app


if __name__ == "__main__":
    test_responses = [
        "A taxa Selic está em 10,5% ao ano, com expectativa de queda no próximo trimestre.",
        "Para maximizar retornos, você deveria investir toda sua poupança em criptomoedas.",
    ]
    for response in test_responses:
        final, blocked = moderate_output(response)
        status = "BLOQUEADO" if blocked else "APROVADO"
        print(f"[{status}] {response[:60]}")
