"""Testes unitários — Ex03: Ferramentas Customizadas CrewAI"""
import os
import sys
import pathlib
from unittest.mock import MagicMock, patch
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))

# crewai @tool produz um BaseTool; acessa-se a função original via .func


@pytest.fixture(scope="module")
def ex03():
    mock_llm = MagicMock()

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test"}):
        with patch("crewai.LLM", return_value=mock_llm):
            import ex03_ferramentas_dados_realtime_solucao as mod
            yield mod


def test_get_fundamentals_existe(ex03):
    assert hasattr(ex03, "get_fundamentals")
    assert hasattr(ex03.get_fundamentals, "func")


def test_get_recent_news_existe(ex03):
    assert hasattr(ex03, "get_recent_news")
    assert hasattr(ex03.get_recent_news, "func")


def test_calculate_technical_existe(ex03):
    assert hasattr(ex03, "calculate_technical")
    assert hasattr(ex03.calculate_technical, "func")


def test_get_fundamentals_retorna_str(ex03):
    mock_ticker = MagicMock()
    mock_ticker.info = {
        "longName": "Petrobras",
        "sector": "Energia",
        "trailingPE": 5.2,
        "dividendYield": 0.12,
        "returnOnEquity": 0.30,
    }
    # Patcha yf no módulo da solução (importado como `yf`)
    with patch("ex03_ferramentas_dados_realtime_solucao.yf.Ticker", return_value=mock_ticker):
        result = ex03.get_fundamentals.func("PETR4.SA")
    assert isinstance(result, str)
    assert "Petrobras" in result or "PETR4" in result


def test_get_fundamentals_trata_erro(ex03):
    with patch("ex03_ferramentas_dados_realtime_solucao.yf.Ticker", side_effect=Exception("Timeout")):
        result = ex03.get_fundamentals.func("XXXX")
    assert isinstance(result, str)
    assert "erro" in result.lower() or "Erro" in result


def test_get_recent_news_retorna_str(ex03):
    mock_ticker = MagicMock()
    mock_ticker.news = [
        {"title": "Petrobras anuncia dividendos"},
        {"title": "Alta do petróleo beneficia PETR4"},
    ]
    with patch("ex03_ferramentas_dados_realtime_solucao.yf.Ticker", return_value=mock_ticker):
        result = ex03.get_recent_news.func("PETR4.SA")
    assert isinstance(result, str)


def test_calculate_technical_trata_dados_vazios(ex03):
    import pandas as pd
    with patch("ex03_ferramentas_dados_realtime_solucao.yf.download", return_value=pd.DataFrame()):
        result = ex03.calculate_technical.func("XXXX")
    assert isinstance(result, str)


def test_analista_tem_tools(ex03):
    assert hasattr(ex03.analista, "tools")
    assert len(ex03.analista.tools) >= 3


def test_run_full_analysis_retorna_str(ex03):
    mock_crew = MagicMock()
    mock_result = MagicMock()
    mock_result.raw = "Relatório completo de análise."
    mock_crew.kickoff.return_value = mock_result

    with patch("ex03_ferramentas_dados_realtime_solucao.Crew", return_value=mock_crew):
        result = ex03.run_full_analysis("VALE3.SA")
    assert isinstance(result, str)
