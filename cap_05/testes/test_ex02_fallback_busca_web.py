"""Testes unitários — Ex02: Fallback para Busca Web"""
import os
import sys
import pathlib
from unittest.mock import MagicMock, patch
import pytest
from langchain_core.messages import AIMessage, HumanMessage

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))


@pytest.fixture(scope="module")
def ex02():
    mock_llm = MagicMock()
    mock_llm.return_value = AIMessage(content="0.8")
    mock_llm.invoke.return_value = AIMessage(content="Resposta mock")

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test"}):
        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            import ex02_fallback_busca_web_solucao as mod
            yield mod


def test_relevance_threshold_definido(ex02):
    assert hasattr(ex02, "RELEVANCE_THRESHOLD")
    assert 0 < ex02.RELEVANCE_THRESHOLD < 1


def test_evaluate_retrieval_lista_vazia(ex02):
    assert ex02.evaluate_retrieval([]) is False


def test_evaluate_retrieval_score_alto(ex02):
    assert ex02.evaluate_retrieval([("doc1", 0.8), ("doc2", 0.6)]) is True


def test_evaluate_retrieval_score_baixo(ex02):
    assert ex02.evaluate_retrieval([("doc1", 0.3), ("doc2", 0.2)]) is False


def test_evaluate_retrieval_no_limiar(ex02):
    result = ex02.evaluate_retrieval([("doc", ex02.RELEVANCE_THRESHOLD)])
    assert result is True


def test_app_compilado(ex02):
    assert ex02.app is not None


def test_run_query_retorna_dict_com_chaves(ex02):
    mock_state = {
        "messages": [AIMessage(content="Faturamento: R$500k")],
        "source": "base_interna",
        "relevance_score": 0.85,
        "query": "faturamento 2024",
        "context": "",
    }
    with patch.object(ex02.app, "invoke", return_value=mock_state):
        result = ex02.run_query("Qual o faturamento?")
    assert "resposta" in result
    assert "fonte" in result
    assert "score" in result


def test_run_query_fonte_base_interna(ex02):
    mock_state = {
        "messages": [AIMessage(content="R$900k")],
        "source": "base_interna",
        "relevance_score": 0.9,
        "query": "faturamento",
        "context": "",
    }
    with patch.object(ex02.app, "invoke", return_value=mock_state):
        result = ex02.run_query("Qual o faturamento total?")
    assert result["fonte"] == "base_interna"
