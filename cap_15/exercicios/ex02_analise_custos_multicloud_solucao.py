"""
cap_15 — Solução Exercício 2: Análise de Custos Multi-Cloud
Dificuldade: Médio | Tempo estimado: ~45 min
"""
import json
import pathlib
import sys
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))
from tools import get_aws_costs, get_azure_costs, get_gcp_costs  # noqa: E402

REPORT_PATH = pathlib.Path(__file__).parent.parent / "cost_comparison.json"

# Latência média (região próxima) e SLA de disponibilidade publicados pelos
# providers para instâncias de VM de propósito geral com múltiplas AZs —
# valores ilustrativos, atualize com benchmarks reais para decisões de produção.
PROVIDER_FACTORS = {
    "aws": {"estimated_latency_ms": 15, "sla_pct": 99.99},
    "azure": {"estimated_latency_ms": 18, "sla_pct": 99.95},
    "gcp": {"estimated_latency_ms": 16, "sla_pct": 99.99},
}


class WorkloadSpec:
    def __init__(self, vcpu: int, memory_gb: float, storage_gb: int, region: str = "us-east"):
        self.vcpu = vcpu
        self.memory_gb = memory_gb
        self.storage_gb = storage_gb
        self.region = region


def _extract_cost_usd(tool_result: str) -> float | None:
    """Extrai o valor US$ X.XX da string retornada pelas tools de custo."""
    import re

    match = re.search(r"US\$\s*([\d.]+)", tool_result)
    return float(match.group(1)) if match else None


def get_comparable_costs(spec: WorkloadSpec, service_names: dict[str, str] | None = None) -> dict:
    """Retorna estimativas de custo dos 3 providers para o workload, normalizadas
    para USD/hora, junto com fatores de latência e SLA."""
    service_names = service_names or {
        "aws": "AmazonEC2",
        "azure": "Virtual Machines",
        "gcp": "Compute Engine",
    }
    days = 30
    raw = {
        "aws": get_aws_costs.invoke({"service": service_names["aws"], "days": days}),
        "azure": get_azure_costs.invoke({"service": service_names["azure"], "days": days}),
        "gcp": get_gcp_costs.invoke({"service": service_names["gcp"], "days": days}),
    }

    result = {}
    for provider, texto in raw.items():
        custo_total = _extract_cost_usd(texto)
        cost_per_hour = round(custo_total / (days * 24), 6) if custo_total else None
        result[provider] = {
            "cost_usd_hour": cost_per_hour,
            "raw": texto,
            **PROVIDER_FACTORS[provider],
        }
    return result


def recommend_provider(costs: dict) -> dict:
    """Recomenda o provider mais barato entre os que têm custo disponível, com justificativa."""
    disponiveis = {p: c for p, c in costs.items() if c["cost_usd_hour"] is not None}
    if not disponiveis:
        return {"provider": None, "reason": "Nenhum provider retornou custo (credenciais não configuradas)."}

    melhor = min(disponiveis, key=lambda p: disponiveis[p]["cost_usd_hour"])
    c = disponiveis[melhor]
    return {
        "provider": melhor,
        "cost_usd_hour": c["cost_usd_hour"],
        "reason": (
            f"{melhor} tem o menor custo/hora (US$ {c['cost_usd_hour']}) entre os providers com dados "
            f"disponíveis, com SLA de {c['sla_pct']}% e latência estimada de {c['estimated_latency_ms']}ms."
        ),
    }


if __name__ == "__main__":
    spec = WorkloadSpec(vcpu=2, memory_gb=4, storage_gb=50)
    costs = get_comparable_costs(spec)
    recomendacao = recommend_provider(costs)

    report = {
        "timestamp": datetime.now().isoformat(),
        "workload": vars(spec),
        "costs": costs,
        "recommendation": recomendacao,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Relatório salvo em {REPORT_PATH}")
    print(f"Recomendação: {recomendacao['reason']}")
