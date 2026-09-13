"""
cap_10 — Exercício 2: Protegendo o Webhook Receiver
Dificuldade: Médio | Tempo estimado: ~45 min

TAREFA:
Implemente um servidor Flask que recebe webhooks do Langflow com verificação
de assinatura HMAC para garantir autenticidade das requisições.

Requisitos:
1. Gere um WEBHOOK_SECRET e configure-o no Langflow e no .env.
2. Valide o header X-Langflow-Signature usando HMAC-SHA256.
3. Rejeite requisições sem assinatura válida com HTTP 401.
4. Implemente rate limiting simples: máximo 10 req/min por IP.
5. Registre todas as tentativas (válidas e inválidas) em cap_10/webhook.log.
"""
import os
import hmac
import hashlib
import logging
from collections import defaultdict
from time import time
from flask import Flask, request, jsonify, abort
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").encode()
logging.basicConfig(filename="cap_10/webhook.log", level=logging.INFO)

# Rate limiting: {ip: [timestamps]}
request_log: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 10
RATE_WINDOW = 60.0


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verifica a assinatura HMAC-SHA256 do webhook."""
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


@app.route("/webhook/langflow", methods=["POST"])
def langflow_webhook():
    ip = request.remote_addr
    if not check_rate_limit(ip):
        logging.warning(f"Rate limit excedido: {ip}")
        abort(429)

    signature = request.headers.get("X-Langflow-Signature", "")
    if WEBHOOK_SECRET and not verify_signature(request.data, signature):
        logging.warning(f"Assinatura inválida de {ip}")
        abort(401)

    logging.info(f"Webhook válido de {ip}")
    payload = request.get_json()
    # TODO: processe o payload do Langflow
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(port=8080, debug=False)
