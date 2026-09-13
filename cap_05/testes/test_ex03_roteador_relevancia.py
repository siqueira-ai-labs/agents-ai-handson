"""Testes unitários — Ex03: Roteador com Avaliação de Relevância"""
import os
import sys
import pathlib
from unittest.mock import MagicMock, patch
import pytest
from langchain_core.messages import AIMessage, HumanMessage

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))


@pytest.fixture(scope="module")
def ex03():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="Resposta mock")
    mock_llm.with_structured_output.return_value = mock_llm

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test"}):
        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            import ex03_roteador_relevancia_solucao as mod
            yield mod


def test_confidence_threshold_definido(ex03):
    assert hasattr(ex03, "CONFIDENCE_THRESHOLD")
    assert 0 < ex03.CONFIDENCE_THRESHOLD <= 1.0


def test_routing_decision_model(ex03):
    from ex03_roteador_relevancia_solucao import RoutingDecision
    decision = RoutingDecision(tool="consultar_vendas", confidence=0.9, reasoning="Contém dados de vendas")
    assert decision.tool == "consultar_vendas"
    assert decision.confidence == 0.9


def test_routing_decision_confidence_bounds(ex03):
    from ex03_roteador_relevancia_solucao import RoutingDecision
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        RoutingDecision(tool="x", confidence=1.5, reasoning="")
    with pytest.raises(ValidationError):
        RoutingDecision(tool="x", confidence=-0.1, reasoning="")


def test_tools_description_definido(ex03):
    assert hasattr(ex03, "TOOLS_DESCRIPTION")
    assert len(ex03.TOOLS_DESCRIPTION) >= 3


def test_routing_log_existe(ex03):
    assert hasattr(ex03, "routing_log")
    assert isinstance(ex03.routing_log, list)


def test_app_compilado(ex03):
    assert ex03.app is not None


def test_run_query_retorna_dict_com_chaves(ex03):
    from ex03_roteador_relevancia_solucao import RoutingDecision
    mock_decision = RoutingDecision(tool="consultar_vendas", confidence=0.9, reasoning="dados de vendas")
    mock_state = {
        "messages": [AIMessage(content="R$900k no Q3")],
        "routing_decision": mock_decision.model_dump(),
        "query": "Q3",
        "context": "",
    }
    with patch.object(ex03.app, "invoke", return_value=mock_state):
        result = ex03.run_query("Qual foi o Q3?")
    assert "resposta" in result
    assert "tool" in result
    assert "confidence" in result
    assert "reasoning" in result


def test_fallback_quando_confianca_baixa(ex03):
    from ex03_roteador_relevancia_solucao import RoutingDecision
    mock_decision = RoutingDecision(tool="busca_web", confidence=0.4, reasoning="não encontrado")
    mock_state = {
        "messages": [AIMessage(content="Informação genérica")],
        "routing_decision": mock_decision.model_dump(),
        "query": "tendências 2030",
        "context": "",
    }
    with patch.object(ex03.app, "invoke", return_value=mock_state):
        result = ex03.run_query("Quais as tendências para 2030?")
    assert result["confidence"] == 0.4
