"""Testes unitários — Ex01: Agente FAQ no LangGraph"""
import os
import sys
import pathlib
from unittest.mock import MagicMock, patch
import pytest
from langchain_core.messages import AIMessage, HumanMessage

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "exercicios"))


@pytest.fixture(scope="module")
def ex01():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="Resposta do LLM", tool_calls=[])
    mock_llm.return_value = AIMessage(content="Resposta do LLM", tool_calls=[])

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test"}):
        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            import ex01_novo_agente_solucao as mod
            yield mod


def test_faq_db_tem_5_entradas(ex01):
    assert len(ex01.FAQ_DB) >= 5


def test_faq_lookup_encontra_horario(ex01):
    result = ex01.faq_lookup("Qual o horário de atendimento?")
    assert result is not None
    assert "horário" in result.lower() or "8h" in result or "segunda" in result.lower()


def test_faq_lookup_retorna_none_para_desconhecido(ex01):
    result = ex01.faq_lookup("problema técnico com processador")
    assert result is None


def test_faq_lookup_cancelamento(ex01):
    result = ex01.faq_lookup("como faço para cancelamento")
    assert result is not None


def test_faq_agent_node_retorna_dict_com_messages(ex01):
    state = {"messages": [HumanMessage(content="Qual o prazo de entrega?")]}
    result = ex01.faq_agent_node(state)
    assert "messages" in result
    assert len(result["messages"]) > 0


def test_faq_response_contem_prefixo_faq(ex01):
    state = {"messages": [HumanMessage(content="prazo de entrega")]}
    result = ex01.faq_agent_node(state)
    content = result["messages"][0].content
    assert "[FAQ]" in content


def test_app_compilado(ex01):
    assert ex01.app is not None


def test_run_chatbot_faq_retorna_str(ex01):
    mock_state = {"messages": [AIMessage(content="[FAQ] Atendemos de segunda a sexta.", tool_calls=[])]}
    with patch.object(ex01.app, "invoke", return_value=mock_state):
        result = ex01.run_chatbot("horário de atendimento")
    assert isinstance(result, str)
    assert len(result) > 0


def test_router_node_faq_path(ex01):
    state = {"messages": [HumanMessage(content="Qual o horário de funcionamento?")]}
    result = ex01.router_node(state)
    assert result == "faq_agent"


def test_router_node_llm_path(ex01):
    state = {"messages": [HumanMessage(content="Meu produto está com problema de driver.")]}
    result = ex01.router_node(state)
    assert result == "llm_agent"
