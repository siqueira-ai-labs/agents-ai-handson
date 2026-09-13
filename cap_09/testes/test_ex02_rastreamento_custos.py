"""Testes unitários — Ex02: Rastreamento de Custos com Langfuse"""
import os
import pathlib
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))


@pytest.fixture(scope="module")
def ex02():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="Resposta de teste")

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test", "LANGFUSE_PUBLIC_KEY": "pk-test", "LANGFUSE_SECRET_KEY": "sk-test"}):
        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            import ex02_rastreamento_custos_solucao as mod
            yield mod


def test_modulo_importavel(ex02):
    assert ex02 is not None


def test_grafo_tem_dois_nos(ex02):
    nomes = list(ex02.graph.nodes.keys())
    assert "triagem" in nomes
    assert "final" in nomes


def test_run_two_step_uma_unica_invocacao(ex02):
    fake_state = {"messages": [AIMessage(content="resposta final")]}
    fake_handler = MagicMock()
    with patch.object(ex02.app, "invoke", return_value=fake_state) as mock_invoke:
        resultado = ex02.run_two_step("pergunta", fake_handler)
    assert resultado == "resposta final"
    mock_invoke.assert_called_once()
    _, kwargs = mock_invoke.call_args
    assert kwargs["config"]["callbacks"] == [fake_handler]


def test_get_daily_cost_report_agrega_tokens_e_custo(ex02):
    obs1 = SimpleNamespace(trace_id="t1", usage=SimpleNamespace(total=100), calculated_total_cost=0.001)
    obs2 = SimpleNamespace(trace_id="t1", usage=SimpleNamespace(total=50), calculated_total_cost=0.0005)
    obs3 = SimpleNamespace(trace_id="t2", usage=SimpleNamespace(total=200), calculated_total_cost=0.002)

    fake_client = MagicMock()
    fake_client.get_observations.return_value = SimpleNamespace(data=[obs1, obs2, obs3])

    report = ex02.get_daily_cost_report(fake_client, "2026-01-15")

    assert report["date"] == "2026-01-15"
    assert report["total_traces"] == 2
    assert report["total_observations"] == 3
    assert report["total_tokens"] == 350
    assert report["total_cost_usd"] == pytest.approx(0.0035)


def test_get_daily_cost_report_sem_observacoes(ex02):
    fake_client = MagicMock()
    fake_client.get_observations.return_value = SimpleNamespace(data=[])
    report = ex02.get_daily_cost_report(fake_client, "2026-01-15")
    assert report["total_traces"] == 0
    assert report["total_tokens"] == 0
    assert report["total_cost_usd"] == 0
