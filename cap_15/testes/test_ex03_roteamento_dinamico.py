"""Testes unitários — Ex03: Roteamento Dinâmico por Custo e Latência (com fakeredis)"""
import pathlib
import sys

import fakeredis
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))

import ex03_roteamento_dinamico_solucao as ex03


@pytest.fixture
def fake_client():
    return fakeredis.FakeStrictRedis()


def test_modulo_importavel():
    assert ex03 is not None


def test_record_and_get_latency_history(fake_client):
    ex03.record_latency("nemotron-70b", 1.5, client=fake_client)
    ex03.record_latency("nemotron-70b", 2.0, client=fake_client)
    historico = ex03.get_latency_history("nemotron-70b", client=fake_client)
    assert historico == [2.0, 1.5]  # lpush insere no início


def test_record_latency_mantem_apenas_ultimas_10(fake_client):
    for i in range(15):
        ex03.record_latency("llama-8b", float(i), client=fake_client)
    historico = ex03.get_latency_history("llama-8b", client=fake_client)
    assert len(historico) == 10


def test_select_best_provider_sem_historico_usa_default(fake_client):
    # Sem histórico, ambos usam latência default (5.0s) — desempata por custo:
    # llama-8b é mais barato, então tem score maior.
    escolhido = ex03.select_best_provider(client=fake_client)
    assert escolhido == "llama-8b"


def test_select_best_provider_leva_latencia_em_conta(fake_client):
    # O termo de custo (1/cost) domina a fórmula para custos na casa de
    # frações de centavo — só uma diferença de latência muito grande
    # (nemotron respondendo em ~50 microssegundos vs llama-8b no default de
    # 5s) é suficiente para reverter a escolha baseada só em custo.
    for _ in range(5):
        ex03.record_latency("nemotron-70b", 0.00005, client=fake_client)
    escolhido = ex03.select_best_provider(client=fake_client)
    assert escolhido == "nemotron-70b"


def test_metrics_endpoint_retorna_dados_por_provider(fake_client, monkeypatch):
    monkeypatch.setattr(ex03, "r", fake_client)
    ex03.record_latency("nemotron-70b", 1.0, client=fake_client)
    client = ex03.app_flask.test_client()
    resp = client.get("/metrics")
    data = resp.get_json()
    assert resp.status_code == 200
    assert "nemotron-70b" in data
    assert "llama-8b" in data
    assert data["nemotron-70b"]["samples"] == 1
