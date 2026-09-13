"""Testes unitários — Ex02: Processo Hierárquico CrewAI"""
import os
import sys
import pathlib
from unittest.mock import MagicMock, patch
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))


@pytest.fixture(scope="module")
def ex02():
    mock_llm = MagicMock()
    mock_crew = MagicMock()
    mock_result = MagicMock()
    mock_result.raw = "Relatório de análise mock."
    mock_crew.kickoff.return_value = mock_result

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test"}):
        with patch("crewai.LLM", return_value=mock_llm):
            import ex02_processo_hierarquico_solucao as mod
            yield mod


def test_modulo_importavel(ex02):
    assert ex02 is not None


def test_agentes_definidos(ex02):
    assert hasattr(ex02, "pesquisador")
    assert hasattr(ex02, "analista_fundamental")
    assert hasattr(ex02, "analista_risco")


def test_build_crew_sequential_existe(ex02):
    assert callable(ex02.build_crew_sequential)


def test_build_crew_hierarchical_existe(ex02):
    assert callable(ex02.build_crew_hierarchical)


def test_run_analysis_existe(ex02):
    assert callable(ex02.run_analysis)


def test_run_analysis_retorna_str(ex02):
    mock_crew = MagicMock()
    mock_result = MagicMock()
    mock_result.raw = "Relatório de análise."
    mock_crew.kickoff.return_value = mock_result

    with patch.object(ex02, "build_crew_hierarchical", return_value=mock_crew):
        result = ex02.run_analysis("PETR4.SA", mode="hierarchical")
    assert isinstance(result, str)


def test_manager_llm_definido(ex02):
    assert hasattr(ex02, "manager_llm")
    assert ex02.manager_llm is not None


def test_analista_risco_tem_role(ex02):
    assert "risco" in ex02.analista_risco.role.lower() or "risk" in ex02.analista_risco.role.lower()
