"""Testes unitários — Ex03: Alertas de Latência com AgentOps"""
import os
import pathlib
import sys
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))


@pytest.fixture(scope="module")
def ex03():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="ok", tool_calls=[])
    mock_llm.bind_tools.return_value = mock_llm

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test"}, clear=False):
        os.environ.pop("AGENTOPS_API_KEY", None)
        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            import ex03_alertas_latencia_solucao as mod
            yield mod


@pytest.fixture(autouse=True)
def isolar_arquivos_de_metrica(ex03, tmp_path, monkeypatch):
    monkeypatch.setattr(ex03, "METRICS_FILE", tmp_path / "metrics.jsonl")


def test_modulo_importavel(ex03):
    assert ex03 is not None


@pytest.mark.parametrize(
    "data,percentil,esperado",
    [
        ([1, 2, 3, 4, 5], 50, 3.0),
        ([], 95, 0.0),
        ([10.0], 99, 10.0),
    ],
)
def test_calculate_percentile(ex03, data, percentil, esperado):
    assert ex03.calculate_percentile(data, percentil) == esperado


def test_check_alerts_latencia_alta(ex03):
    metrics = [{"latency_sec": 11.0}, {"latency_sec": 12.0}, {"latency_sec": 9.0}]
    alertas = ex03.check_alerts(metrics)
    assert any("Latência" in a for a in alertas)


def test_check_alerts_taxa_erro_alta(ex03):
    metrics = [{"error": "boom"}] * 10
    alertas = ex03.check_alerts(metrics)
    assert any("erros" in a for a in alertas)


def test_check_alerts_sem_problemas(ex03):
    metrics = [{"latency_sec": 1.0, "error": None}] * 10
    assert ex03.check_alerts(metrics) == []


def test_instrumented_run_registra_metrica_de_sucesso(ex03, monkeypatch):
    monkeypatch.setattr(ex03, "run_agent", lambda q: "resposta")
    metric = ex03.instrumented_run("pergunta")
    assert metric["error"] is None
    assert metric["latency_sec"] >= 0
    salvas = ex03.load_metrics()
    assert len(salvas) == 1


def test_instrumented_run_registra_metrica_de_erro(ex03, monkeypatch):
    def falha(q):
        raise RuntimeError("falhou")

    monkeypatch.setattr(ex03, "run_agent", falha)
    metric = ex03.instrumented_run("pergunta")
    assert metric["error"] == "falhou"


def test_monitor_loop_roda_max_iterations(ex03, monkeypatch):
    chamadas = []
    monkeypatch.setattr(ex03, "run_agent", lambda q: chamadas.append(q))
    ex03.monitor_loop(["q1", "q2"], interval=0, max_iterations=1)
    assert chamadas == ["q1", "q2"]
    assert len(ex03.load_metrics()) == 2
