"""Testes unitários — Ex01: Controle de Recursão"""
import os
import sys
import pathlib
from unittest.mock import MagicMock, patch
import pytest
from langchain_core.messages import AIMessage
from langgraph.errors import GraphRecursionError

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))


@pytest.fixture(scope="module")
def ex01():
    mock_llm = MagicMock()
    mock_llm.return_value = AIMessage(content="Cotação PETR4.SA: R$ 38.00", tool_calls=[])
    mock_llm.bind_tools.return_value = mock_llm

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test"}):
        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            import ex01_controle_recursao_solucao as mod
            yield mod


def test_modulo_importavel(ex01):
    assert ex01 is not None


def test_run_with_recursion_limit_existe(ex01):
    assert hasattr(ex01, "run_with_recursion_limit")
    assert callable(ex01.run_with_recursion_limit)


def test_retorna_mensagem_amigavel_em_recursion_error(ex01):
    with patch.object(ex01.app, "invoke", side_effect=GraphRecursionError("limit")):
        result = ex01.run_with_recursion_limit("query complexa", limit=5)
    assert "limite" in result.lower() or "iterações" in result.lower()


def test_retorna_string(ex01):
    mock_state = {"messages": [AIMessage(content="Resposta ok", tool_calls=[])]}
    with patch.object(ex01.app, "invoke", return_value=mock_state):
        result = ex01.run_with_recursion_limit("Qual a cotação?")
    assert isinstance(result, str)


def test_config_tem_recursion_limit(ex01):
    captured = {}

    def fake_invoke(input_, config=None):
        captured["config"] = config
        return {"messages": [AIMessage(content="ok", tool_calls=[])]}

    with patch.object(ex01.app, "invoke", side_effect=fake_invoke):
        ex01.run_with_recursion_limit("teste", limit=5)

    assert captured.get("config", {}).get("recursion_limit") == 5
