"""
cap_09 — Solução Exercício 3: Alertas de Latência com AgentOps
Dificuldade: Difícil | Tempo estimado: ~2-3h
"""
import json
import logging
import os
import pathlib
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))
from agent import run_agent  # noqa: E402

METRICS_FILE = Path(__file__).parent.parent / "metrics.jsonl"
LATENCY_P95_THRESHOLD_SEC = 10.0
ERROR_RATE_THRESHOLD = 0.05
MONITOR_INTERVAL_SEC = 60

logger = logging.getLogger("cap09.alertas")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.FileHandler(str(Path(__file__).parent.parent / "alertas.log"))
    _handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(_handler)


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


def _agentops_enabled() -> bool:
    return bool(os.getenv("AGENTOPS_API_KEY"))


def instrumented_run(query: str) -> dict:
    """Executa uma consulta do agente, mede a latência e registra a métrica.
    Instrumenta com AgentOps quando AGENTOPS_API_KEY está configurada; caso
    contrário, a medição de latência/erro continua funcionando localmente."""
    trace = None
    if _agentops_enabled():
        import agentops

        trace = agentops.start_trace(trace_name="cap09-instrumented-run", tags=["cap_09", "latencia"])

    start = time.time()
    error = None
    try:
        run_agent(query)
    except Exception as e:
        error = str(e)
    latency = time.time() - start

    if trace is not None:
        import agentops
        from agentops.enums import TraceState

        agentops.end_trace(trace, end_state=TraceState.ERROR if error else TraceState.SUCCESS)

    metric = {"timestamp": time.time(), "query": query, "latency_sec": latency, "error": error}
    with METRICS_FILE.open("a") as f:
        f.write(json.dumps(metric) + "\n")

    alerts = check_alerts(load_metrics())
    for alert in alerts:
        print(alert)
        logger.warning(alert)

    return metric


def monitor_loop(queries: list[str], interval: float = MONITOR_INTERVAL_SEC, max_iterations: int | None = None):
    """Executa consultas periodicamente, verificando alertas a cada ciclo."""
    if _agentops_enabled():
        import agentops

        agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"))

    iteration = 0
    while max_iterations is None or iteration < max_iterations:
        for query in queries:
            instrumented_run(query)
        iteration += 1
        if max_iterations is None or iteration < max_iterations:
            time.sleep(interval)


if __name__ == "__main__":
    print(f"Monitor de alertas — verificando a cada {MONITOR_INTERVAL_SEC}s")
    monitor_loop(
        ["Qual o preço atual da ação da Tesla (TSLA)?"],
        interval=MONITOR_INTERVAL_SEC,
        max_iterations=1,
    )
