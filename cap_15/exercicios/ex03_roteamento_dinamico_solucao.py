"""
cap_15 — Solução Exercício 3: Roteamento Dinâmico por Custo e Latência
Dificuldade: Difícil | Tempo estimado: ~2-3h
"""
import json
import os
import time

import redis
from dotenv import load_dotenv
from flask import Flask, jsonify
from langchain_openai import ChatOpenAI

load_dotenv()

PROVIDERS = {
    "nemotron-70b": {
        "model": "nvidia/llama-3.1-nemotron-70b-instruct:free",
        "cost_per_1k_tokens": 0.00035,
    },
    "llama-8b": {
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "cost_per_1k_tokens": 0.00005,
    },
}

HISTORY_SIZE = 10
r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

app_flask = Flask(__name__)


def _history_key(provider_key: str) -> str:
    return f"latency_history:{provider_key}"


def record_latency(provider_key: str, latency: float, client=None) -> None:
    """Registra a latência no Redis, mantendo só as últimas HISTORY_SIZE medições
    (moving window via lista + LTRIM)."""
    client = client if client is not None else r  # lookup dinâmico, não um default fixado na definição
    key = _history_key(provider_key)
    client.lpush(key, latency)
    client.ltrim(key, 0, HISTORY_SIZE - 1)


def get_latency_history(provider_key: str, client=None) -> list[float]:
    client = client if client is not None else r
    key = _history_key(provider_key)
    return [float(v) for v in client.lrange(key, 0, -1)]


def measure_latency(provider_key: str, prompt: str, client=None) -> tuple[str, float]:
    client = client if client is not None else r
    """Invoca o provider e mede a latência. Retorna (resposta, latency_sec)."""
    cfg = PROVIDERS[provider_key]
    llm = ChatOpenAI(
        model=cfg["model"],
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
    )
    start = time.perf_counter()
    response = llm.invoke(prompt)
    latency = time.perf_counter() - start
    record_latency(provider_key, latency, client=client)
    return response.content, latency


def select_best_provider(client=None) -> str:
    """Seleciona o provider com maior score composto custo+latência (moving average)."""
    client = client if client is not None else r
    scores = {}
    for key, cfg in PROVIDERS.items():
        history = get_latency_history(key, client=client)
        avg_latency = sum(history) / len(history) if history else 5.0
        cost = cfg["cost_per_1k_tokens"]
        scores[key] = 0.6 * (1 / avg_latency) + 0.4 * (1 / (cost + 1e-9))
    return max(scores, key=scores.get)


@app_flask.route("/metrics")
def metrics():
    data = {}
    for key in PROVIDERS:
        history = get_latency_history(key)
        data[key] = {
            "avg_latency_sec": sum(history) / len(history) if history else None,
            "samples": len(history),
            "cost_per_1k": PROVIDERS[key]["cost_per_1k_tokens"],
        }
    return jsonify(data)


if __name__ == "__main__":
    print("Roteamento dinâmico — iniciando benchmark...")
    prompt = "Explique o conceito de serverless em uma linha."
    for _ in range(3):
        provider = select_best_provider()
        answer, latency = measure_latency(provider, prompt)
        print(f"[{provider}] {latency:.2f}s → {answer[:60]}")
    print("\nIniciando dashboard em http://localhost:5001/metrics")
    app_flask.run(port=5001, debug=False)
