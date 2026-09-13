"""Testes unitários — Ex02: Análise de Custos Multi-Cloud"""
import pathlib
import sys
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))

import ex02_analise_custos_multicloud_solucao as ex02


def test_modulo_importavel():
    assert ex02 is not None


def test_extract_cost_usd_encontra_valor():
    assert ex02._extract_cost_usd("[AWS] EC2: US$ 12.34 (últimos 30 dias)") == 12.34


def test_extract_cost_usd_retorna_none_sem_match():
    assert ex02._extract_cost_usd("[AWS] Não foi possível consultar") is None


def test_get_comparable_costs_normaliza_para_usd_hora():
    spec = ex02.WorkloadSpec(vcpu=2, memory_gb=4, storage_gb=50)
    with patch("ex02_analise_custos_multicloud_solucao.get_aws_costs") as m_aws, \
         patch("ex02_analise_custos_multicloud_solucao.get_azure_costs") as m_azure, \
         patch("ex02_analise_custos_multicloud_solucao.get_gcp_costs") as m_gcp:
        m_aws.invoke.return_value = "[AWS] EC2: US$ 720.00 (últimos 30 dias)"
        m_azure.invoke.return_value = "[Azure] VM: US$ 360.00 (últimos 30 dias)"
        m_gcp.invoke.return_value = "[GCP] Não foi possível consultar custos"

        custos = ex02.get_comparable_costs(spec)

    # 720 USD / (30*24h) = 1.0 USD/h
    assert custos["aws"]["cost_usd_hour"] == 1.0
    assert custos["azure"]["cost_usd_hour"] == 0.5
    assert custos["gcp"]["cost_usd_hour"] is None


def test_recommend_provider_escolhe_o_mais_barato():
    costs = {
        "aws": {"cost_usd_hour": 1.0, "sla_pct": 99.99, "estimated_latency_ms": 15},
        "azure": {"cost_usd_hour": 0.5, "sla_pct": 99.95, "estimated_latency_ms": 18},
        "gcp": {"cost_usd_hour": None, "sla_pct": 99.99, "estimated_latency_ms": 16},
    }
    recomendacao = ex02.recommend_provider(costs)
    assert recomendacao["provider"] == "azure"
    assert "azure" in recomendacao["reason"]


def test_recommend_provider_sem_dados_disponiveis():
    costs = {
        "aws": {"cost_usd_hour": None, "sla_pct": 99.99, "estimated_latency_ms": 15},
        "azure": {"cost_usd_hour": None, "sla_pct": 99.95, "estimated_latency_ms": 18},
        "gcp": {"cost_usd_hour": None, "sla_pct": 99.99, "estimated_latency_ms": 16},
    }
    recomendacao = ex02.recommend_provider(costs)
    assert recomendacao["provider"] is None
