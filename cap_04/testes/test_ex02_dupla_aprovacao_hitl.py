"""Testes unitários — Ex02: Dupla Aprovação HITL"""
import os
import sys
import pathlib
from unittest.mock import MagicMock, patch, call
import pytest
from langchain_core.messages import AIMessage, ToolMessage

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "projeto"))


@pytest.fixture(scope="module")
def ex02():
    mock_llm = MagicMock()
    mock_llm.return_value = AIMessage(content="Cotação: R$38.00", tool_calls=[])
    mock_llm.bind_tools.return_value = mock_llm

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test"}):
        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            import ex02_dupla_aprovacao_hitl_solucao as mod
            yield mod


def test_modulo_importavel(ex02):
    assert ex02 is not None


def test_app_compilado(ex02):
    assert ex02.app is not None


def test_run_dupla_aprovacao_existe(ex02):
    assert hasattr(ex02, "run_dupla_aprovacao")
    assert callable(ex02.run_dupla_aprovacao)


def test_sem_tool_calls_retorna_conteudo(ex02):
    state = {"messages": [AIMessage(content="Sem ferramenta", tool_calls=[])]}
    with patch.object(ex02.app, "invoke", return_value=state):
        config = {"configurable": {"thread_id": "t1"}}
        result = ex02.run_dupla_aprovacao("pergunta", config)
    assert result == "Sem ferramenta"


def test_cancelamento_antes_da_execucao(ex02):
    ai_msg = AIMessage(content="", tool_calls=[{"name": "get_stock_price", "args": {}, "id": "1"}])
    state1 = {"messages": [ai_msg]}
    with patch.object(ex02.app, "invoke", return_value=state1):
        config = {"configurable": {"thread_id": "t2"}}
        result = ex02.run_dupla_aprovacao("query", config, approve_exec=False)
    assert "cancelada" in result.lower() or "get_stock_price" in result


def test_cancelamento_apos_resultado_bruto(ex02):
    ai_msg = AIMessage(content="", tool_calls=[{"name": "get_stock_price", "args": {}, "id": "1"}])
    tool_msg = ToolMessage(content="PETR4: R$38.00", tool_call_id="1")
    final_msg = AIMessage(content="Análise completa", tool_calls=[])
    state1 = {"messages": [ai_msg]}
    state2 = {"messages": [ai_msg, tool_msg, final_msg]}

    invoke_calls = [state1, state2]
    with patch.object(ex02.app, "invoke", side_effect=invoke_calls):
        config = {"configurable": {"thread_id": "t3"}}
        result = ex02.run_dupla_aprovacao("query", config, approve_exec=True, approve_result=False)
    assert "PETR4" in result or "bruto" in result.lower() or "38" in result


def test_dupla_aprovacao_completa(ex02):
    ai_msg = AIMessage(content="", tool_calls=[{"name": "get_stock_price", "args": {}, "id": "1"}])
    tool_msg = ToolMessage(content="PETR4: R$38.00", tool_call_id="1")
    final_msg = AIMessage(content="Análise: PETR4 está em R$38.00", tool_calls=[])
    state1 = {"messages": [ai_msg]}
    state2 = {"messages": [ai_msg, tool_msg]}
    state3 = {"messages": [ai_msg, tool_msg, final_msg]}

    with patch.object(ex02.app, "invoke", side_effect=[state1, state2, state3]):
        config = {"configurable": {"thread_id": "t4"}}
        result = ex02.run_dupla_aprovacao("query", config, approve_exec=True, approve_result=True)
    assert "Análise" in result or "38" in result
