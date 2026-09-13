"""
cap_15 — Exercício 3: Roteamento Dinâmico por Custo e Latência
Dificuldade: Difícil | Tempo estimado: ~2-3h

TAREFA:
Implemente um roteador dinâmico que seleciona automaticamente o provider de
LLM baseado em custo/token E latência medida em tempo real.

Requisitos:
1. Mantenha um histórico de latência (últimas 10 chamadas) por provider em Redis.
2. Calcule um score composto: score = 0.6 * (1/latency) + 0.4 * (1/cost_per_token).
3. Selecione o provider com maior score.
4. Atualize o score a cada chamada (moving average).
5. Implemente um dashboard simples (JSON endpoint Flask) com métricas ao vivo.
"""
import os
import time
import json
from collections import deque
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

# Histórico de latência por provider (últimas 10 medições)
latency_history: dict[str, deque] = {k: deque(maxlen=10) for k in PROVIDERS}

app_flask = Flask(__name__)


def measure_latency(provider_key: str, prompt: str) -> tuple[str, float]:
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
    latency_history[provider_key].append(latency)
    return response.content, latency


def select_best_provider() -> str:
    """Seleciona o provider com maior score composto custo+latência."""
    scores = {}
    for key, cfg in PROVIDERS.items():
        history = list(latency_history[key])
        avg_latency = sum(history) / len(history) if history else 5.0
        cost = cfg["cost_per_1k_tokens"]
        scores[key] = 0.6 * (1 / avg_latency) + 0.4 * (1 / (cost + 1e-9))
    return max(scores, key=scores.get)


@app_flask.route("/metrics")
def metrics():
    data = {}
    for key in PROVIDERS:
        history = list(latency_history[key])
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
