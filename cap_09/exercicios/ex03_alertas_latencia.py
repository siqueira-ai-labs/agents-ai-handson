"""
cap_09 — Exercício 3: Alertas de Latência com AgentOps
Dificuldade: Difícil | Tempo estimado: ~2-3h

TAREFA:
Configure alertas automáticos que disparam quando a latência do agente
ultrapassa um limiar ou quando a taxa de erros excede 5%.

Requisitos:
1. Instrumente o agente com AgentOps para capturar latência por nó do grafo.
2. Implemente um monitor que verifica métricas a cada 60 segundos.
3. Envie alerta (print + log) quando: latência_p95 > 10s OU error_rate > 5%.
4. Calcule percentis (p50, p95, p99) de latência a partir do histórico.
5. Persista o histórico de métricas em cap_09/metrics.jsonl.
"""
import os
import json
import time
import statistics
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

METRICS_FILE = Path("cap_09/metrics.jsonl")
LATENCY_P95_THRESHOLD_SEC = 10.0
ERROR_RATE_THRESHOLD = 0.05
MONITOR_INTERVAL_SEC = 60


def calculate_percentile(data: list[float], percentile: float) -> float:
    """Calcula um percentil de uma lista de valores."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    index = (percentile / 100) * (len(sorted_data) - 1)
    lower = int(index)
    upper = lower + 1
    if upper >= len(sorted_data):
        return sorted_data[-1]
    return sorted_data[lower] + (index - lower) * (sorted_data[upper] - sorted_data[lower])


def load_metrics() -> list[dict]:
    """Carrega métricas do arquivo JSONL."""
    if not METRICS_FILE.exists():
        return []
    return [json.loads(line) for line in METRICS_FILE.read_text().splitlines() if line]


def check_alerts(metrics: list[dict]) -> list[str]:
    """Retorna lista de alertas ativos baseado nas métricas."""
    alerts = []
    latencies = [m["latency_sec"] for m in metrics if "latency_sec" in m]
    errors = [m for m in metrics if m.get("error")]

    if latencies:
        p95 = calculate_percentile(latencies, 95)
        if p95 > LATENCY_P95_THRESHOLD_SEC:
            alerts.append(f"⚠️  Latência P95 = {p95:.1f}s (limiar: {LATENCY_P95_THRESHOLD_SEC}s)")

    if metrics:
        error_rate = len(errors) / len(metrics)
        if error_rate > ERROR_RATE_THRESHOLD:
            alerts.append(f"🔴 Taxa de erros = {error_rate:.1%} (limiar: {ERROR_RATE_THRESHOLD:.0%})")

    return alerts


# TODO: implemente a instrumentação do agente com AgentOps
# TODO: implemente o loop de monitoramento


if __name__ == "__main__":
    print(f"Monitor de alertas — verificando a cada {MONITOR_INTERVAL_SEC}s")
    # TODO: execute o loop de monitoramento
