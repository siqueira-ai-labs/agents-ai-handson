"""
cap_10 — Solução Exercício 2: Protegendo o Webhook Receiver
Dificuldade: Médio | Tempo estimado: ~45 min
"""
import hashlib
import hmac
import logging
import os
import pathlib
from collections import defaultdict
from time import time

from dotenv import load_dotenv
from flask import Flask, abort, jsonify, request

load_dotenv()

app = Flask(__name__)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").encode()

LOG_PATH = pathlib.Path(__file__).parent.parent / "webhook.log"
logger = logging.getLogger("cap10.webhook")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.FileHandler(str(LOG_PATH))
    _handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_handler)

# Rate limiting: {ip: [timestamps]}
request_log: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 10
RATE_WINDOW = 60.0


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verifica a assinatura HMAC-SHA256 do webhook."""
    if not signature:
        return False
    expected = hmac.new(WEBHOOK_SECRET, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


def check_rate_limit(ip: str) -> bool:
    """Retorna True se dentro do limite, False se excedeu."""
    now = time()
    request_log[ip] = [t for t in request_log[ip] if now - t < RATE_WINDOW]
    if len(request_log[ip]) >= RATE_LIMIT:
        return False
    request_log[ip].append(now)
    return True


def process_langflow_payload(payload: dict) -> dict:
    """Extrai os campos relevantes do payload de webhook do Langflow."""
    outputs = payload.get("outputs", [])
    mensagens = []
    for output in outputs:
        for result in output.get("outputs", []) if isinstance(output, dict) else []:
            texto = result.get("results", {}).get("message", {}).get("text")
            if texto:
                mensagens.append(texto)
    return {
        "flow_id": payload.get("flow_id") or payload.get("session_id"),
        "mensagens": mensagens,
    }


@app.route("/webhook/langflow", methods=["POST"])
def langflow_webhook():
    ip = request.remote_addr
    if not check_rate_limit(ip):
        logger.warning(f"Rate limit excedido: {ip}")
        abort(429)

    signature = request.headers.get("X-Langflow-Signature", "")
    if WEBHOOK_SECRET and not verify_signature(request.data, signature):
        logger.warning(f"Assinatura inválida de {ip}")
        abort(401)

    logger.info(f"Webhook válido de {ip}")
    payload = request.get_json(silent=True) or {}
    processed = process_langflow_payload(payload)
    return jsonify({"status": "ok", "processed": processed})


if __name__ == "__main__":
    app.run(port=8080, debug=False)
