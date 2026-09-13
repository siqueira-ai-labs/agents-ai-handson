"""
cap_15 — Exercício 2: Análise de Custos Multi-Cloud
Dificuldade: Médio | Tempo estimado: ~45 min

TAREFA:
Expanda o agente para comparar o custo do mesmo workload nos 3 providers
e recomendar a opção mais econômica.

Requisitos:
1. Implemente get_comparable_costs(workload_spec) que consulta os 3 providers.
2. Normalize os custos para USD/hora.
3. O agente deve recomendar o provider mais barato com justificativa.
4. Inclua fatores além do custo: latência estimada, disponibilidade SLA.
5. Salve o relatório de comparação em cap_15/cost_comparison.json.
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

REPORT_PATH = "cap_15/cost_comparison.json"


class WorkloadSpec:
    def __init__(self, vcpu: int, memory_gb: float, storage_gb: int, region: str = "us-east"):
        self.vcpu = vcpu
        self.memory_gb = memory_gb
        self.storage_gb = storage_gb
        self.region = region


def get_comparable_costs(spec: WorkloadSpec) -> dict:
    """Retorna estimativas de custo dos 3 providers para o workload."""
    # TODO: implemente consultas reais via SDKs ou use APIs de pricing públicas
    # AWS: https://pricing.us-east-1.amazonaws.com/
    # Azure: https://prices.azure.com/api/retail/prices
    # GCP: https://cloudpricingcalculator.appspot.com/
    return {
        "aws": {"cost_usd_hour": 0.0, "service": "EC2", "instance_type": "TBD"},
        "azure": {"cost_usd_hour": 0.0, "service": "VM", "size": "TBD"},
        "gcp": {"cost_usd_hour": 0.0, "service": "Compute Engine", "machine_type": "TBD"},
    }


if __name__ == "__main__":
    spec = WorkloadSpec(vcpu=2, memory_gb=4, storage_gb=50)
    costs = get_comparable_costs(spec)
    report = {"timestamp": datetime.now().isoformat(), "workload": vars(spec), "costs": costs}
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Relatório salvo em {REPORT_PATH}")
