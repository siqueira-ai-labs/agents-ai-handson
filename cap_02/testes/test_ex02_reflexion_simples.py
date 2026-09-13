"""
Testes unitários — Ex02: Reflexion Simples (ReAct + nó de reflexão)
"""
import json
import os
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage


# ── Fixture de importação com mocks ──────────────────────────────────────────

@pytest.fixture(scope="module")
def ex02():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content='{"approved": true, "feedback": "Ótima resposta."}')
    mock_llm.bind_tools.return_value = mock_llm

    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test", "TAVILY_API_KEY": "tvly-test"}):
        with patch("langchain_openai.ChatOpenAI", return_value=mock_llm):
            import ex02_reflexion_simples_solucao as mod
            mod.llm = mock_llm
            mod.llm_with_tools = mock_llm
            yield mod


# ── Testes: constantes e tipos ────────────────────────────────────────────────

def test_max_iterations_definido(ex02):
    assert hasattr(ex02, "MAX_ITERATIONS")
    assert ex02.MAX_ITERATIONS > 0


def test_state_tem_campo_messages(ex02):
    hints = ex02.State.__annotations__
    assert "messages" in hints


def test_state_tem_campo_iteration(ex02):
    hints = ex02.State.__annotations__
    assert "iteration" in hints


def test_state_tem_campo_approved(ex02):
    hints = ex02.State.__annotations__
    assert "approved" in hints


def test_reflection_output_campos(ex02):
    ro = ex02.ReflectionOutput(approved=True, feedback="OK")
    assert ro.approved is True
    assert ro.feedback == "OK"


# ── Testes: funções de roteamento ─────────────────────────────────────────────

def test_should_reflect_sem_tool_calls_vai_para_reflection(ex02):
    state = {
        "messages": [AIMessage(content="Resposta sem ferramentas")],
        "iteration": 0,
        "approved": False,
    }
    assert ex02.should_reflect(state) == "reflection"


def test_should_reflect_com_tool_calls_vai_para_tools(ex02):
    msg = AIMessage(content="")
    msg.tool_calls = [{"name": "calculator", "args": {}, "id": "tc_01"}]
    state = {"messages": [msg], "iteration": 0, "approved": False}
    assert ex02.should_reflect(state) == "tools"


def test_should_continue_aprovado_retorna_end(ex02):
    state = {"messages": [], "iteration": 1, "approved": True}
    assert ex02.should_continue(state) == "__end__"


def test_should_continue_nao_aprovado_dentro_do_limite(ex02):
    state = {"messages": [], "iteration": 1, "approved": False}
    assert ex02.should_continue(state) == "agent"


def test_should_continue_limite_atingido_retorna_end(ex02):
    state = {"messages": [], "iteration": ex02.MAX_ITERATIONS, "approved": False}
    assert ex02.should_continue(state) == "__end__"


# ── Testes: reflection_node ───────────────────────────────────────────────────

def test_reflection_node_aprovado_nao_adiciona_mensagem(ex02):
    ex02.llm.invoke.return_value = AIMessage(content='{"approved": true, "feedback": "Perfeito."}')
    state = {
        "messages": [AIMessage(content="Boa resposta aqui.")],
        "iteration": 0,
        "approved": False,
    }
    result = ex02.reflection_node(state)
    assert result["approved"] is True
    assert result["messages"] == []


def test_reflection_node_nao_aprovado_adiciona_human_message(ex02):
    ex02.llm.invoke.return_value = AIMessage(
        content='{"approved": false, "feedback": "Precisa melhorar."}'
    )
    state = {
        "messages": [AIMessage(content="Resposta fraca.")],
        "iteration": 0,
        "approved": False,
    }
    result = ex02.reflection_node(state)
    assert result["approved"] is False
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], HumanMessage)
    assert "Precisa melhorar" in result["messages"][0].content


def test_reflection_node_incrementa_iteration(ex02):
    ex02.llm.invoke.return_value = AIMessage(content='{"approved": true, "feedback": "OK"}')
    state = {"messages": [AIMessage(content="texto")], "iteration": 2, "approved": False}
    result = ex02.reflection_node(state)
    assert result["iteration"] == 3


def test_reflection_node_json_malformado_nao_levanta(ex02):
    ex02.llm.invoke.return_value = AIMessage(content="resposta sem json")
    state = {"messages": [AIMessage(content="texto")], "iteration": 0, "approved": False}
    result = ex02.reflection_node(state)
    assert "approved" in result
    assert "iteration" in result


# ── Testes: estrutura do grafo ────────────────────────────────────────────────

def test_build_reflection_graph_retorna_grafo(ex02):
    app = ex02.build_reflection_graph()
    assert app is not None


def test_grafo_tem_no_agent(ex02):
    app = ex02.build_reflection_graph()
    assert "agent" in list(app.nodes)


def test_grafo_tem_no_reflection(ex02):
    app = ex02.build_reflection_graph()
    assert "reflection" in list(app.nodes)


def test_grafo_tem_no_tools(ex02):
    app = ex02.build_reflection_graph()
    assert "tools" in list(app.nodes)
